# File: roottest/python/ttree/PyROOT_ttreetests.py
# Author: Wim Lavrijsen (LBNL, WLavrijsen@lbl.gov)
# Created: 10/13/06
# Last: 10/13/06

"""TTree reading/writing unit tests for PyROOT package."""

import os, sys, unittest
from ROOT import *

__all__ = [
   'TTree1ReadWriteSimpleObjectsTestCase'
]

gROOT.LoadMacro( "TTreeTypes.C+" )


### Write/Read an std::vector to/from file ===================================
class TTree1ReadWriteSimpleObjectsTestCase( unittest.TestCase ):
   N, M = 5, 10
   fname, tname, ttitle = 'test.root', 'test', 'test tree'

   def test1WriteStdVector( self ):
      """Test writing of a single branched TTree with an std::vector<double>"""

      f = TFile( self.fname, 'RECREATE' )
      t = TTree( self.tname, self.ttitle )
      v = std.vector( 'double' )()
      t.Branch( 'mydata', v.__class__.__name__, v )

      for i in range( self.N ):
         for j in range( self.M ):
            v.push_back( i*self.M+j )
         t.Fill()
         v.clear()
      f.Write()
      f.Close()

   def test2ReadStdVector( self ):
      """Test reading of a single branched TTree with an std::vector<double>"""

      f = TFile( self.fname )
      mytree = f.Get( self.tname )

      i = 0
      for event in mytree:
         for entry in mytree.mydata:
            self.assertEqual( i, int(entry) )
            i += 1
      self.assertEqual( i, self.N * self.M )

      f.Close()

   def test3WriteSomeDataObject( self ):
      """Test writing of a complex data object"""

      f = TFile( self.fname, 'RECREATE' )
      t = TTree( self.tname, self.ttitle )

      d = SomeDataObject()
      t.Branch( 'data', d );

      for i in range( self.N ):
         for j in range( self.M ):
            d.AddFloat( i*self.M+j )

         d.AddTuple( d.GetFloats() )

         t.Fill()

      f.Write()
      f.Close()


   def test4ReadSomeDataObject( self ):
      """Test reading of a complex data object"""

      f = TFile( self.fname )
      mytree = f.Get( self.tname )

      for event in mytree:
         i = 0
         for entry in event.data.GetFloats():
            self.assertEqual( i, int(entry) )
            i += 1

         for mytuple in event.data.GetTuples():
            i = 0
            for entry in mytuple:
               self.assertEqual( i, int(entry) )
               i += 1

      f.Close()

   def test5WriteSomeDataObjectBranched( self ):
      """Test writing of a complex object across different branches"""

      f = TFile( self.fname, 'RECREATE' )
      t = TTree( self.tname, self.ttitle )

      d = SomeDataStruct()
      t.Branch( 'floats', d.Floats )
      t.Branch( 'nlabel', AddressOf( d, 'NLabel' ), 'NLabel/I' )
      t.Branch( 'label',  AddressOf( d, 'Label' ),  'Label/C' )

      for i in range( self.N ):
         for j in range( self.M ):
            d.Floats.push_back( i*self.M+j )

         d.NLabel = i
         d.Label  = '%d' % i

         t.Fill()

      f.Write()
      f.Close()

   def test6ReadSomeDataObjectBranched( self ):
      """Test reading of a complex object across different branches"""

      f = TFile( self.fname )
      mytree = f.Get( self.tname )

      for event in mytree:
         i, j = 0, 0
         for entry in event.floats:
            self.assertEqual( i, int(entry) )
            i += 1

         self.assertEqual( event.Label, str(int(event.NLabel)) )

      f.Close()


## actual test run
if __name__ == '__main__':
   sys.path.append( os.path.join( os.getcwd(), os.pardir ) )
   from MyTextTestRunner import MyTextTestRunner

   loader = unittest.TestLoader()
   testSuite = loader.loadTestsFromModule( sys.modules[ __name__ ] )

   runner = MyTextTestRunner( verbosity = 2 )
   result = not runner.run( testSuite ).wasSuccessful()

   sys.exit( result )
