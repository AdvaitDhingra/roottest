# File: roottest/python/common.py
# Author: Wim Lavrijsen (LBNL, WLavrijsen@lbl.gov)
# Created: 09/24/10
# Last: 02/20/14

__all__ = [ 'pylong', 'maxvalue', 'MyTestCase', 'run_pytest', 'FIXCLING', 'USECPP11' ]

import os, sys, unittest

# add local pytest dir to sys.path to make pytest available
toplevel = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(toplevel, 'pytest'))


if sys.hexversion >= 0x3000000:
   pylong = int
   maxvalue = sys.maxsize

   class MyTestCase( unittest.TestCase ):
      def shortDescription( self ):
         desc = str(self)
         doc_first_line = None

         if self._testMethodDoc:
            doc_first_line = self._testMethodDoc.split("\n")[0].strip()
         if doc_first_line:
            desc = doc_first_line
         return desc
else:
   pylong = long
   maxvalue = sys.maxint

   class MyTestCase( unittest.TestCase ):
      pass

FIXCLING = '--fixcling' in sys.argv
if 'FIXCLING' in os.environ:
   FIXCLING = os.environ['FIXCLING'] == 'yes'

def usecpp():
   import commands
   (stat, result) = commands.getstatusoutput( 'root-config --has-cxx11 --has-c++11' )
   return not stat and 'yes' in result
USECPP11 = usecpp()
del usecpp


def run_pytest(test_file=None):
    # add local pytest dir to sys.path
    toplevel = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.join(toplevel, 'pytest'))
    import pytest
    import pytest_cov
    # file to run, if any (search used otherwise)
    args = ['--color=no', '--result-log=stdout', '--minimal=yes']
    if test_file: args += [test_file]
    # actual test run
    return pytest.main(args, plugins=[pytest_cov])
