# File: roottest/python/regression/PyROOT_regressiontests.py
# Author: Wim Lavrijsen (LBNL, WLavrijsen@lbl.gov)
# Created: 01/02/07
# Last: 05/04/11

"""Regression tests, lacking a better place, for PyROOT package."""

import sys, os, unittest
sys.path.append( os.path.join( os.getcwd(), os.pardir ) )

try:
   import commands
except ImportError:
   import subprocess as commands
from ROOT import *
from common import *

__all__ = [
   'Regression01TwiceImportStarTestCase',
   'Regression02PyExceptionTestcase',
   'Regression03UserDefinedNewOperatorTestCase',
   'Regression04ThreadingTestCase',
   'Regression05LoKiNamespaceTestCase',
   'Regression06Int64ConversionTestCase',
   'Regression07MatchConstWithProperReturn',
   'Regression08UseNamespaceProperlyInPythonize',
   'Regression09CheckEnumExactMatch',
   'Regression10BreakSmartPtrCircularLoop',
   'Regression10TVector3Pythonize',
   'Regression11CoralAttributeListIterators',
   'Regression12ImportCout',
   'Regression13WriteTGraph',
   'Regression14BaseClassUsing',
   'Regression15TPyException'
]


### "from ROOT import *" done in import-*-ed module ==========================
from Amir import *

class Regression01TwiceImportStarTestCase( MyTestCase ):
   def test1FromROOTImportStarInModule( self ):
      """Test handling of twice 'from ROOT import*'"""

      x = TestTChain()        # TestTChain defined in Amir.py


### TPyException thrown from C++ code ========================================
class Regression02PyExceptionTestcase( MyTestCase ):
   def test1RaiseAndTrapPyException( self ):
      """Test thrown TPyException object processing"""

      gROOT.LoadMacro( "Scott.C+" )

    # test of not overloaded global function
      self.assertRaises( SyntaxError, ThrowPyException )
      try:
         ThrowPyException()
      except SyntaxError:
         self.assertEqual( str(sys.exc_info()[1]), "test error message" )

    # test of overloaded function
      self.assertRaises( SyntaxError, MyThrowingClass.ThrowPyException, 1 )
      try:
         MyThrowingClass.ThrowPyException( 1 )
      except SyntaxError:
         self.assertEqual( str(sys.exc_info()[1]), "overloaded int test error message" )


### By-value return for class that defines operator new ======================
class Regression03UserDefinedNewOperatorTestCase( MyTestCase ):
   def test1CreateTemporary( self ):
      """Test handling of a temporary for user defined operator new"""

      gROOT.LoadMacro( "MuonTileID.C+" )

      if FIXCLING:       # failure b/c of temporaries
         return

      getID()
      getID()                 # used to crash


### Test the condition under which to (not) start the GUI thread =============
class Regression04ThreadingTestCase( MyTestCase ):

   hasThread = gROOT.IsBatch() and 5 or 6   # can't test if no display ...
   noThread  = 5
   
   def test1SpecialCasegROOT( self ):
      """Test the special role that gROOT plays vis-a-vis threading"""

      cmd = sys.executable + "  -c 'import sys, ROOT; ROOT.gROOT; %s "\
            "sys.exit( 5 + int(\"thread\" in ROOT.__dict__) )'"
      if self.hasThread == self.noThread:
         cmd += " - -b"

      stat, out = commands.getstatusoutput( cmd % "" )
      self.assertEqual( os.WEXITSTATUS(stat), self.noThread )

      stat, out = commands.getstatusoutput( cmd % "ROOT.gROOT.SetBatch( 1 );" )
      self.assertEqual( os.WEXITSTATUS(stat), self.noThread )

      stat, out = commands.getstatusoutput( cmd % "ROOT.gROOT.SetBatch( 0 );" )
      self.assertEqual( os.WEXITSTATUS(stat), self.noThread )

      stat, out = commands.getstatusoutput(
         cmd % "ROOT.gROOT.ProcessLine( \"cout << 42 << endl;\" ); " )
      self.assertEqual( os.WEXITSTATUS(stat), self.hasThread )

      stat, out = commands.getstatusoutput( cmd % "ROOT.gDebug;" )
      self.assertEqual( os.WEXITSTATUS(stat), self.hasThread )

   def test2ImportStyles( self ):
      """Test different import styles vis-a-vis threading"""

      cmd = sys.executable + " -c 'import sys; %s ;"\
            "import ROOT; sys.exit( 5 + int(\"thread\" in ROOT.__dict__) )'"
      if self.hasThread == self.noThread:
         cmd += " - -b"

      stat, out = commands.getstatusoutput( cmd % "from ROOT import *" )
      self.assertEqual( os.WEXITSTATUS(stat), self.hasThread )

      stat, out = commands.getstatusoutput( cmd % "from ROOT import gROOT" )
      self.assertEqual( os.WEXITSTATUS(stat), self.noThread )

      stat, out = commands.getstatusoutput( cmd % "from ROOT import gDebug" )
      self.assertEqual( os.WEXITSTATUS(stat), self.hasThread )

   def test3SettingOfBatchMode( self ):
      """Test various ways of preventing GUI thread startup"""

      cmd = sys.executable + " -c '%s import ROOT, sys; sys.exit( 5+int(\"thread\" in ROOT.__dict__ ) )'"
      if self.hasThread == self.noThread:
         cmd += " - -b"

      stat, out = commands.getstatusoutput( (cmd % 'from ROOT import *;') + ' - -b' )
      self.assertEqual( os.WEXITSTATUS(stat), self.noThread )

      stat, out = commands.getstatusoutput(
         cmd % 'import ROOT; ROOT.PyConfig.StartGuiThread = 0;' )
      self.assertEqual( os.WEXITSTATUS(stat), self.noThread )

      stat, out = commands.getstatusoutput(
         cmd % 'from ROOT import PyConfig; PyConfig.StartGuiThread = 0; from ROOT import gDebug;' )
      self.assertEqual( os.WEXITSTATUS(stat), self.noThread )

      stat, out = commands.getstatusoutput(
         cmd % 'from ROOT import PyConfig; PyConfig.StartGuiThread = 1; from ROOT import gDebug;' )
      self.assertEqual( os.WEXITSTATUS(stat), self.hasThread )

      stat, out = commands.getstatusoutput(
         cmd % 'from ROOT import gROOT; gROOT.SetBatch( 1 ); from ROOT import *;' )
      self.assertEqual( os.WEXITSTATUS(stat), self.noThread )

      if not gROOT.IsBatch():               # can't test if no display ...
         stat, out = commands.getstatusoutput(
            cmd % 'from ROOT import gROOT; gROOT.SetBatch( 0 ); from ROOT import *;' )
         self.assertEqual( os.WEXITSTATUS(stat), self.hasThread )


### Test the proper resolution of a template with namespaced parameter =======
class Regression05LoKiNamespaceTestCase( MyTestCase ):
   def test1TemplateWithNamespaceParameter( self ):
      """Test name resolution of template with namespace parameter"""

      rcp = 'const LHCb::Particle*'

      gROOT.LoadMacro( 'LoKiNamespace.C+' )

      self.assertEqual( LoKi.Constant( rcp ).__name__, 'LoKi::Constant<%s>' % rcp )
      self.assertEqual(
         LoKi.BooleanConstant( rcp ).__name__, 'LoKi::BooleanConstant<%s>' % rcp )

### Test conversion of int64 objects to ULong64_t and ULong_t ================
class Regression06Int64ConversionTestCase( MyTestCase ):
   limit1  = 4294967295
   limit1L = pylong(4294967295)

   def test1IntToULongTestCase( self ):
      """Test conversion of Int(64) limit values to unsigned long"""

      gROOT.LoadMacro( 'ULongLong.C+' )

      self.assertEqual( self.limit1,  ULongFunc( self.limit1 ) )
      self.assertEqual( self.limit1L, ULongFunc( self.limit1 ) )
      self.assertEqual( self.limit1L, ULongFunc( self.limit1L ) )
      self.assertEqual( maxvalue + 2, ULongFunc( maxvalue + 2 ) )

   def test2IntToULongLongTestCase( self ):
      """Test conversion of Int(64) limit values to unsigned long long"""

      self.assertEqual( self.limit1,  ULong64Func( self.limit1 ) )
      self.assertEqual( self.limit1L, ULong64Func( self.limit1 ) )
      self.assertEqual( self.limit1L, ULong64Func( self.limit1L ) )
      self.assertEqual( maxvalue + 2, ULong64Func( maxvalue + 2 ) )


### Proper match-up of return type and overloaded function ===================
class Regression07MatchConstWithProperReturn( MyTestCase ):
   def test1OverloadOrderWithProperReturn( self ):
      """Test return type against proper overload w/ const and covariance"""

      if FIXCLING:       # failure b/c of no exact match
         return

      gROOT.LoadMacro( "Scott2.C+" )

      self.assertEqual( MyOverloadOneWay().gime(), 1 )
      self.assertEqual( MyOverloadTheOtherWay().gime(), "aap" )


### Don't forget namespace when looking up a class in Pythonize! =============
class Regression08UseNamespaceProperlyInPythonize( MyTestCase ):
   def test1UseNamespaceInIteratorPythonization( self ):
      """Do not crash on classes with iterators in a namespace"""

      gROOT.LoadMacro( "Marco.C" )
      self.assert_( ns.MyClass )


### enum type conversions (used to fail exact match in CINT) =================
class Regression09CheckEnumExactMatch( MyTestCase ):
   def test1CheckEnumCalls( self ):
      """Be able to pass enums as function arguments"""

      gROOT.LoadMacro( "Till.C+" )
      a = Monkey()
      self.assertEqual( fish, a.testEnum1( fish ) )
      self.assertEqual( cow,  a.testEnum2( cow ) )
      self.assertEqual( bird, a.testEnum3( bird ) )
      self.assertEqual( marsupilami, a.testEnum4( marsupilami ) )
      self.assertEqual( marsupilami, a.testEnum4( Long(marsupilami) ) )

### "smart" classes that return themselves on dereference cause a loop =======
class Regression10BreakSmartPtrCircularLoop( MyTestCase ):
   def test1VerifyNoLoopt( self ):
      """Smart class that returns itself on dereference should not loop"""

      gROOT.LoadMacro( "Scott3.C+" )
      a = MyTooSmartClass()
      self.assertRaises( AttributeError, getattr, a, 'DoesNotExist' )


### test pythonization of TVector3 ===========================================
class Regression10TVector3Pythonize( MyTestCase ):
   def test1TVector3( self ):
      """Verify TVector3 pythonization"""

      v = TVector3( 1., 2., 3.)
      self.assertEqual( list(v), [1., 2., 3. ] )


### test pythonization coral::AttributeList iterators ========================
class Regression11CoralAttributeListIterators( MyTestCase ):
   def test1IterateWithBaseIterator( self ):
      """Verify that the correct base class iterators is picked up"""

      if FIXCLING:       # failure b/c of temporaries
         return

      gROOT.LoadMacro( "CoralAttributeList.C+" )

      a = coral_pyroot_regression.AttributeList()

      a.extend( "i", "int" )
      self.assertEqual( a.size(), 1 )
      self.assertEqual( a.begin(), a.begin() )
      self.assertNotEqual( a.begin(), a.end() )

      b = a.begin()
      e = a.end()
      self.assertNotEqual( a, e )

      b.__preinc__()
      self.assertEqual( b, e )
      self.assertNotEqual( b, a.begin() )


### importing cout should not result in printed errors =======================
class Regression12ImportCout( MyTestCase ):
   def test1ImportCout( self ):
      """Test that ROOT.cout does not cause error messages"""

      if FIXCLING:
         return

      import ROOT
      c = ROOT.cout


### importing cout should not result in printed errors =======================
class Regression13WriteTGraph( MyTestCase ):
   def test1WriteTGraph( self ):
      """Write a TGraph object and read it back correctly"""

      gr = TGraph()
      ff = TFile( "test.root", "RECREATE" )
      ff.WriteObject( gr, "grname", "" )
      gr2 = TGraph()
      ff.GetObject( "grname", gr2 )
      os.remove( "test.root" )


### 'using' base class data members should make them accessible ==============
class Regression14BaseClassUsing( MyTestCase ):
   def test1AccessUsingBaseClassDataMember( self ):
      """Access a base class data member made availabe by 'using'"""

      if FIXCLING:
         return

      p = TPySelector()
      str( p.fInput )        # segfaults in case of failure


### TPyException had troubles due to its base class of std::exception ========
class Regression15TPyException( MyTestCase ):
   def test1PythonAccessToTPyException( self ):
      """Load TPyException into python and make sure its usable"""

      e = PyROOT.TPyException()
      self.assert_( e )
      self.assertEqual( e.what(), "python exception" )


## actual test run
if __name__ == '__main__':
   from MyTextTestRunner import MyTextTestRunner

   loader = unittest.TestLoader()
   testSuite = loader.loadTestsFromModule( sys.modules[ __name__ ] )

   runner = MyTextTestRunner( verbosity = 2 )
   result = not runner.run( testSuite ).wasSuccessful()

   sys.exit( result )
