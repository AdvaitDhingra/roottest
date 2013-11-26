# File: roottest/python/common.py
# Author: Wim Lavrijsen (LBNL, WLavrijsen@lbl.gov)
# Created: 09/24/10
# Last: 11/26/13

__all__ = [ 'pylong', 'maxvalue', 'MyTestCase', 'FIXCLING', 'USECPP11' ]

import os, sys, unittest

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

