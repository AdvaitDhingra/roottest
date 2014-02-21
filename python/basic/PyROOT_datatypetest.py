# File: roottest/python/basic/PyROOT_datatypetests.py
# Author: Wim Lavrijsen (LBNL, WLavrijsen@lbl.gov)
# Created: 05/11/05
# Last: 02/20/14

"""Data type conversion unit tests for PyROOT package."""

import os, sys
sys.path.append( os.path.join( os.getcwd(), os.pardir ) )

from common import *
from pytest import raises

# Compatibility notes: set_char() and set_uchar() raise a TypeError in PyROOT
# when handed a string argument, but a ValueError in cppyy. Further, in cppyy
# all object participate in memory regulation, but in PyROOT only TObject
# deriveds (which receive a recursive call).

PYTEST_MIGRATION = True

def setup_module(mod):
    import sys, os
    sys.path.append( os.path.join( os.getcwd(), os.pardir ) )
    err = os.system("make DataTypes_C")
    if err:
        raise OSError("'make' failed (see stderr)")


class TestClassDATATYPES:
    def setup_class(cls):
        import cppyy
        cls.test_dct = "DataTypes_C"
        cls.datatypes = cppyy.load_reflection_info(cls.test_dct)
        cls.N = cppyy.gbl.N

    def test01_load_reflection_cache(self):
        """Test whether loading a refl. info twice results in the same object"""
        import cppyy
        lib2 = cppyy.load_reflection_info(self.test_dct)
        assert self.datatypes is lib2

    def test02_instance_data_read_access(self):
        """Read access to instance public data and verify values"""

        import cppyy, sys
        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        assert isinstance(c, CppyyTestData)

        # reading boolean type
        assert c.m_bool == False

        # reading char types
        assert c.m_char  == 'a'
        assert c.m_schar == 'b'
        assert c.m_uchar == 'c'

        # reading integer types
        assert c.m_short   == -11; assert c.get_short_cr()   == -11
        assert c.m_ushort  ==  11; assert c.get_ushort_cr()  ==  11
        assert c.m_int     == -22; assert c.get_int_cr()     == -22
        assert c.m_uint    ==  22; assert c.get_uint_cr()    ==  22
        assert c.m_long    == -33; assert c.get_long_cr()    == -33
        assert c.m_ulong   ==  33; assert c.get_ulong_cr()   ==  33
        assert c.m_llong   == -44; assert c.get_llong_cr()   == -44
        assert c.m_ullong  ==  44; assert c.get_ullong_cr()  ==  44
        assert c.m_long64  == -55; assert c.get_long64_cr()  == -55
        assert c.m_ulong64 ==  55; assert c.get_ulong64_cr() ==  55

        # reading floating point types
        assert round(c.m_float          + 66.,  5) == 0
        assert round(c.get_float_cr()   + 66.,  5) == 0
        assert round(c.m_double         + 77., 11) == 0
        assert round(c.get_double_cr()  + 77., 11) == 0
        assert round(c.m_ldouble        + 88., 24) == 0
        assert round(c.get_ldouble_cr() + 88., 24) == 0

        # reading of enum types
        assert c.m_enum == CppyyTestData.kNothing
        assert c.m_enum == c.kNothing

        # reading of boolean array
        for i in range(self.N):
            assert c.m_bool_array[i]        ==   bool(i%2)
            assert c.get_bool_array()[i]    ==   bool(i%2)
            assert c.m_bool_array2[i]       ==   bool((i+1)%2)
            assert c.get_bool_array2()[i]   ==   bool((i+1)%2)

        # reading of integer array types
        names = [ 'short', 'ushort',    'int', 'uint',    'long',  'ulong']
        alpha = [(-1, -2),   (3, 4), (-5, -6), (7, 8), (-9, -10), (11, 12)]
        for j in range(self.N):
            assert getattr(c, 'm_%s_array'    % names[i])[i]   == alpha[i][0]*i
            assert getattr(c, 'get_%s_array'  % names[i])()[i] == alpha[i][0]*i
            assert getattr(c, 'm_%s_array2'   % names[i])[i]   == alpha[i][1]*i
            assert getattr(c, 'get_%s_array2' % names[i])()[i] == alpha[i][1]*i

        # reading of floating point array types
        for k in range(self.N):
            assert round(c.m_float_array[k]   + 13.*k, 5) == 0
            assert round(c.m_float_array2[k]  + 14.*k, 5) == 0
            assert round(c.m_double_array[k]  + 15.*k, 8) == 0
            assert round(c.m_double_array2[k] + 16.*k, 8) == 0

        # out-of-bounds checks
        raises(IndexError, c.m_short_array.__getitem__,  self.N)
        raises(IndexError, c.m_ushort_array.__getitem__, self.N)
        raises(IndexError, c.m_int_array.__getitem__,    self.N)
        raises(IndexError, c.m_uint_array.__getitem__,   self.N)
        raises(IndexError, c.m_long_array.__getitem__,   self.N)
        raises(IndexError, c.m_ulong_array.__getitem__,  self.N)
        raises(IndexError, c.m_float_array.__getitem__,  self.N)
        raises(IndexError, c.m_double_array.__getitem__, self.N)

        # can not access an instance member on the class
        if not PYTEST_MIGRATION:
            raises(ReferenceError, getattr, CppyyTestData, 'm_bool')
            raises(ReferenceError, getattr, CppyyTestData, 'm_int')

            assert not hasattr(CppyyTestData, 'm_bool')
            assert not hasattr(CppyyTestData, 'm_int')

        c.__destruct__()

    def test03_instance_data_write_access(self):
        """Write access to instance public data and verify values"""

        import cppyy, sys
        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        assert isinstance(c, CppyyTestData)

        # boolean types through functions
        c.set_bool(True);
        assert c.get_bool() == True
        c.set_bool(0);     assert c.get_bool() == False

        # boolean types through data members
        c.m_bool = True;   assert c.get_bool() == True
        c.set_bool(True);  assert c.m_bool     == True
        c.m_bool = 0;      assert c.get_bool() == False
        c.set_bool(0);     assert c.m_bool     == False

        raises(ValueError, 'c.set_bool(10)')

        # char types through functions
        c.set_char('c');     assert c.get_char_cr()  == 'c'
        c.set_char_cr('d');  assert c.get_char()     == 'd'
        c.set_schar('e');    assert c.get_schar_cr() == 'e'
        c.set_schar_cr('f'); assert c.get_schar()    == 'f'
        c.set_uchar('g');    assert c.get_uchar_cr() == 'g'
        c.set_uchar_cr('h'); assert c.get_uchar()    == 'h'

        # char types through data members
        c.m_char = 'b';   assert c.get_char()  ==     'b'
        c.m_char = 40;    assert c.get_char()  == chr(40)
        c.set_char('c');  assert c.m_char      ==     'c'
        c.set_char(41);   assert c.m_char      == chr(41)
        c.m_schar = 'd';  assert c.get_schar() ==     'd'
        c.m_schar = 42;   assert c.get_schar() == chr(42)
        c.set_schar('e'); assert c.m_schar     ==     'e'
        c.set_schar(43);  assert c.m_schar     == chr(43)
        c.m_uchar = 'f';  assert c.get_uchar() ==     'f'
        c.m_uchar = 44;   assert c.get_uchar() == chr(44)
        c.set_uchar('g'); assert c.m_uchar     ==     'g'
        c.set_uchar(45);  assert c.m_uchar     == chr(45)

        raises(TypeError,  'c.set_char("string")')
        raises(ValueError, 'c.set_char(500)')
        raises(TypeError,  'c.set_uchar("string")')
        raises(ValueError, 'c.set_uchar(-1)')

        # integer types
        names = ['short', 'ushort', 'int', 'uint', 'long', 'ulong', 'llong', 'ullong', 'long64', 'ulong64' ]
        for i in range(len(names)):
            exec 'c.m_%s = %d' % (names[i],i)
            assert eval('c.get_%s()' % names[i]) == i

        for i in range(len(names)):
            exec 'c.set_%s(%d)' % (names[i],2*i)
            assert eval('c.m_%s' % names[i]) == 2*i

        for i in range(len(names)):
            exec 'c.set_%s_cr(%d)' % (names[i],3*i)
            assert eval('c.m_%s' % names[i]) == 3*i

        # float types through functions
        c.set_float(0.123);   assert round(c.get_float()   - 0.123,  5) == 0
        c.set_double(0.456);  assert round(c.get_double()  - 0.456, 11) == 0
        if not FIXCLING:
            c.set_ldouble(0.789); assert round(c.get_ldouble() - 0.789, 24) == 0

        # float types through data members
        c.m_float = 0.123;       assert round(c.get_float()   - 0.123,  5) == 0
        c.set_float(0.234);      assert round(c.m_float       - 0.234,  5) == 0
        c.set_float_cr(0.456);   assert round(c.m_float       - 0.456,  5) == 0
        c.m_double = 0.678;      assert round(c.get_double()  - 0.678, 11) == 0
        c.set_double(0.890);     assert round(c.m_double      - 0.890, 11) == 0
        c.set_double_cr(0.012);  assert round(c.m_double      - 0.012, 11) == 0
        if not FIXCLING:
            c.m_ldouble = 0.345;     assert round(c.get_ldouble() - 0.345, 24) == 0
            c.set_ldouble(0.678);    assert round(c.m_ldouble     - 0.678, 24) == 0
            c.set_ldouble_cr(0.902); assert round(c.m_ldouble     - 0.902, 24) == 0

        # enum types
        c.m_enum = CppyyTestData.kSomething; assert c.get_enum() == c.kSomething
        c.set_enum(CppyyTestData.kLots);     assert c.m_enum     == c.kLots
        c.set_enum_cr(CppyyTestData.kLots ); assert c.m_enum     == c.kLots

        # arrays; there will be pointer copies, so destroy the current ones
        c.destroy_arrays()

        # integer arrays
        names = ['short', 'ushort', 'int', 'uint', 'long', 'ulong']
        import array
        a = range(self.N)
        atypes = ['h', 'H', 'i', 'I', 'l', 'L' ]
        for j in range(len(names)):
            b = array.array(atypes[j], a)
            exec 'c.m_%s_array = b' % names[j]   # buffer copies
            for i in range(self.N):
                assert eval('c.m_%s_array[i]' % names[j]) == b[i]

            exec 'c.m_%s_array2 = b' % names[j]  # pointer copies
            b[i] = 28
            for i in range(self.N):
                assert eval('c.m_%s_array2[i]' % names[j]) == b[i]

        c.__destruct__()

    def test04_array_passing(self):
        """Passing of arrays as function arguments"""

        import cppyy, array, sys
        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        assert isinstance(c, CppyyTestData)

        a = range(self.N)
        # test arrays in mixed order, to give overload resolution a workout
        for t in ['d', 'i', 'f', 'H', 'I', 'h', 'L', 'l' ]:
            b = array.array(t, a)

            # typed passing
            ca = c.pass_array(b)
            assert ca.typecode == b.typecode
            assert len(b) == self.N
            for i in range(self.N):
                assert ca[i] == b[i]

            # void* passing
            ca = eval('c.pass_void_array_%s(b)' % t)
            assert ca.typecode == b.typecode
            assert len(b) == self.N
            for i in range(self.N):
                assert ca[i] == b[i]

        # NULL/None passing (will use short*)
        if not PYTEST_MIGRATION:
            assert not c.pass_array(0)
            raises(Exception, c.pass_array(0).__getitem__, 0)    # raises SegfaultException
            assert not c.pass_array(None)
            raises(Exception, c.pass_array(None).__getitem__, 0) # id.

        c.__destruct__()

    def test05_class_read_access(self):
        """Read access to class public data"""

        import cppyy, sys
        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        assert isinstance(c, CppyyTestData)

        # bool type
        assert c.s_bool             == False
        assert CppyyTestData.s_bool == False

        # char types
        assert CppyyTestData.s_char  == 'c'
        assert c.s_char              == 'c'
        assert c.s_schar             == 's'
        assert CppyyTestData.s_schar == 's'
        assert c.s_uchar             == 'u'
        assert CppyyTestData.s_uchar == 'u'

        # integer types
        assert CppyyTestData.s_short   == -101
        assert c.s_short               == -101
        assert c.s_ushort              ==  255
        assert CppyyTestData.s_ushort  ==  255
        assert CppyyTestData.s_int     == -202
        assert c.s_int                 == -202
        assert c.s_uint                ==  202
        assert CppyyTestData.s_uint    ==  202
        assert CppyyTestData.s_long    == -303L
        assert c.s_long                == -303L
        assert c.s_ulong               ==  303L
        assert CppyyTestData.s_ulong   ==  303L
        assert CppyyTestData.s_llong   == -404L
        assert c.s_llong               == -404L
        assert c.s_ullong              ==  404L
        assert CppyyTestData.s_ullong  ==  404L
        assert CppyyTestData.s_long64  == -505L
        assert c.s_long64              == -505L
        assert c.s_ulong64             ==  505L
        assert CppyyTestData.s_ulong64 ==  505L

        # floating point types
        assert round(CppyyTestData.s_float   + 606.,  5) == 0
        assert round(c.s_float               + 606.,  5) == 0
        assert round(CppyyTestData.s_double  + 707., 11) == 0
        assert round(c.s_double              + 707., 11) == 0
        assert round(CppyyTestData.s_ldouble + 808., 24) == 0
        assert round(c.s_ldouble              + 808., 42) == 0

        assert c.s_enum             == CppyyTestData.kNothing
        assert CppyyTestData.s_enum == CppyyTestData.kNothing

        c.__destruct__()

    def test06_class_data_write_access(self):
        """Write access to class public data"""

        import cppyy, sys
        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        assert isinstance(c, CppyyTestData)

        # bool type
        CppyyTestData.s_bool         = True
        assert c.s_bool             == True
        c.s_bool                     = False
        assert CppyyTestData.s_bool == False

        # char types
        CppyyTestData.s_char          = 'a'
        assert c.s_char              == 'a'
        c.s_char                      = 'b'
        assert CppyyTestData.s_char  == 'b'
        CppyyTestData.s_uchar         = 'c'
        assert c.s_uchar             == 'c'
        c.s_uchar                     = 'd'
        assert CppyyTestData.s_uchar == 'd'
        raises(ValueError, setattr, CppyyTestData, 's_uchar', -1)
        raises(ValueError, setattr, c,             's_uchar', -1)

        # integer types
        c.s_short                       = -102
        assert CppyyTestData.s_short   == -102
        CppyyTestData.s_short           = -203
        assert c.s_short               == -203
        c.s_ushort                      =  127
        assert CppyyTestData.s_ushort  ==  127
        CppyyTestData.s_ushort          =  227
        assert c.s_ushort              ==  227
        CppyyTestData.s_int             = -234
        assert c.s_int                 == -234
        c.s_int                         = -321
        assert CppyyTestData.s_int     == -321
        CppyyTestData.s_uint            = 1234
        assert c.s_uint                == 1234
        c.s_uint                        = 4321
        assert CppyyTestData.s_uint    == 4321
        raises(ValueError, setattr, c,             's_uint', -1)
        raises(ValueError, setattr, CppyyTestData, 's_uint', -1)
        CppyyTestData.s_long            = -87L
        assert c.s_long                == -87L
        c.s_long                        = 876L
        assert CppyyTestData.s_long    == 876L
        CppyyTestData.s_ulong           = 876L
        assert c.s_ulong               == 876L
        c.s_ulong                       = 678L
        assert CppyyTestData.s_ulong   == 678L
        raises(ValueError, setattr, CppyyTestData, 's_ulong', -1)
        raises(ValueError, setattr, c,             's_ulong', -1)
        CppyyTestData.s_long64          = -90
        assert c.s_long64              == -90
        c.s_long64                      = 901
        assert CppyyTestData.s_long64  == 901
        CppyyTestData.s_ulong64         = 901
        c.s_ulong64                    == 901
        c.s_ulong64                     = 321
        assert CppyyTestData.s_ulong64 == 321
        raises( ValueError, setattr, CppyyTestData, 's_ulong64', -1 )
        raises( ValueError, setattr, c,             's_ulong64', -1 )

        # floating point types
        CppyyTestData.s_float                    = -3.1415
        assert round(c.s_float, 5 )             == -3.1415
        c.s_float                                =  3.1415
        assert round(CppyyTestData.s_float, 5 ) ==  3.1415
        import math
        c.s_double                               = -math.pi
        assert CppyyTestData.s_double           == -math.pi
        CppyyTestData.s_double                   =  math.pi
        assert c.s_double                       ==  math.pi
        c.s_ldouble                              = -math.pi
        assert CppyyTestData.s_ldouble          == -math.pi
        CppyyTestData.s_ldouble                  =  math.pi
        assert c.s_ldouble                      ==  math.pi

        if not FIXCLING:
            c.s_enum                     = CppyyTestData.kSomething
            assert CppyyTestData.s_enum == CppyyTestData.kBanana
            CppyyTestData.s_enum         = CppyyTestData.kCitrus
            assert c.s_enum             == CppyyTestData.kCitrus

        c.__destruct__()

    def test07_range_access(self):
        """Integer type ranges"""

        import cppyy, sys
        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        assert isinstance(c, CppyyTestData)

        # TODO: should these be TypeErrors, or should char/bool raise
        #       ValueErrors? In any case, consistency is needed ...
        raises(ValueError, setattr, c, 'm_uint',  -1)
        raises(ValueError, setattr, c, 'm_ulong', -1)

        c.__destruct__()

    def test08_type_conversions(self):
        """Conversions between builtin types"""

        import cppyy, sys
        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        assert isinstance(c, CppyyTestData)

        c.m_double = -1
        assert round(c.m_double + 1.0, 8) == 0

        raises(TypeError, c.m_double,  'c')
        raises(TypeError, c.m_int,     -1.)
        raises(TypeError, c.m_int,      1.)

        c.__destruct__()

    def test09_global_builtin_type(self):
        """Access to a global builtin type"""

        import cppyy
        gbl = cppyy.gbl

        assert gbl.g_int == gbl.get_global_int()

        gbl.set_global_int(32)
        assert gbl.get_global_int() == 32
        # TODO: this failes b/c it's a property of the internal libPyROOT
        # module, not of cppyy.gbl
        if not PYTEST_MIGRATION:
            assert gbl.g_int == 32

        gbl.g_int = 22
        # TODO: this failes b/c it's a property of the internal libPyROOT
        # module, not of cppyy.gbl
        if not PYTEST_MIGRATION:
            assert gbl.get_global_int() == 22
        assert gbl.g_int == 22

    def test10_global_ptr(self):
        """Access of global objects through a pointer"""

        import cppyy
        gbl = cppyy.gbl

        raises(ReferenceError, 'gbl.g_pod.m_int')

        c = gbl.CppyyTestPod()
        c.m_int = 42
        c.m_double = 3.14

        gbl.set_global_pod(c)
        assert gbl.is_global_pod(c)
        assert gbl.g_pod.m_int == 42
        assert gbl.g_pod.m_double == 3.14

        d = gbl.get_global_pod()
        assert gbl.is_global_pod(d)
        assert c == d
        # TODO: in PyROOT, non-TObjects are not mem-regulated
        #assert id(c) == id(d)

        e = gbl.CppyyTestPod()
        e.m_int = 43
        e.m_double = 2.14

        gbl.g_pod = e
        # TODO: in PyROOT, non-TObjects are not mem-regulated
        #assert gbl.is_global_pod(e)
        assert gbl.g_pod.m_int == 43
        assert gbl.g_pod.m_double == 2.14

    def test11_enum(self):
        """Access to enums"""

        import cppyy
        gbl = cppyy.gbl

        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        assert isinstance(c, CppyyTestData)

        # test that the enum is accessible as a type
        if not PYTEST_MIGRATION:
            assert CppyyTestData.what

        assert CppyyTestData.kNothing   ==   6
        assert CppyyTestData.kSomething == 111
        assert CppyyTestData.kLots      ==  42

        if not PYTEST_MIGRATION:
            assert CppyyTestData.what(CppyyTestData.kNothing) == CppyyTestData.kNothing
            assert CppyyTestData.what(6) == CppyyTestData.kNothing
            # TODO: only allow instantiations with correct values (C++11)

        assert c.get_enum() == CppyyTestData.kNothing
        assert c.m_enum == CppyyTestData.kNothing

        c.m_enum = CppyyTestData.kSomething
        assert c.get_enum() == CppyyTestData.kSomething
        assert c.m_enum == CppyyTestData.kSomething

        c.set_enum(CppyyTestData.kLots)
        assert c.get_enum() == CppyyTestData.kLots
        assert c.m_enum == CppyyTestData.kLots

        if not PYTEST_MIGRATION:
            assert c.s_enum == CppyyTestData.s_enum
            assert c.s_enum == CppyyTestData.kNothing
            assert CppyyTestData.s_enum == CppyyTestData.kNothing

            c.s_enum = CppyyTestData.kSomething
            assert c.s_enum == CppyyTestData.s_enum
            assert c.s_enum == CppyyTestData.kSomething
            assert CppyyTestData.s_enum == CppyyTestData.kSomething

        # global enums
        if not PYTEST_MIGRATION:
            assert gbl.EFruit         # test type accessible
            assert gbl.kApple  == 78
            assert gbl.kBanana == 29
            assert gbl.kCitrus == 34

    def test12_string_passing(self):
        """Passing/returning of a const char*"""

        import cppyy
        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        assert c.get_valid_string('aap') == 'aap'
        assert c.get_invalid_string() == ''

    def test13_copy_contructor(self):
        """Copy constructor call"""

        import cppyy
        FourVector = cppyy.gbl.FourVector
        
        t1 = FourVector(1., 2., 3., -4.)
        t2 = FourVector(0., 0., 0.,  0.)
        t3 = FourVector(t1)
  
        assert t1 == t3
        assert t1 != t2
        
        for i in range(4):
            assert t1[i] == t3[i]

    def test14_object_returns(self):
        """Access to and return of PODs"""

        import cppyy

        c = cppyy.gbl.CppyyTestData()

        assert c.m_pod.m_int == 888
        assert c.m_pod.m_double == 3.14

        pod = c.get_pod_val()
        assert pod.m_int == 888
        assert pod.m_double == 3.14

        assert c.get_pod_val_ptr().m_int == 888
        assert c.get_pod_val_ptr().m_double == 3.14
        c.get_pod_val_ptr().m_int = 777
        assert c.get_pod_val_ptr().m_int == 777

        assert c.get_pod_val_ref().m_int == 777
        assert c.get_pod_val_ref().m_double == 3.14
        c.get_pod_val_ref().m_int = 666
        assert c.get_pod_val_ref().m_int == 666

        assert c.get_pod_ptrref().m_int == 666
        assert c.get_pod_ptrref().m_double == 3.14

    def test15_object_arguments(self):
        """Setting and returning of a POD through arguments"""

        import cppyy

        c = cppyy.gbl.CppyyTestData()
        assert c.m_pod.m_int == 888
        assert c.m_pod.m_double == 3.14

        p = cppyy.gbl.CppyyTestPod()
        p.m_int = 123
        assert p.m_int == 123
        p.m_double = 321.
        assert p.m_double == 321.

        c.set_pod_val(p)
        assert c.m_pod.m_int == 123
        assert c.m_pod.m_double == 321.

        c = cppyy.gbl.CppyyTestData()
        c.set_pod_ptr_in(p)
        assert c.m_pod.m_int == 123
        assert c.m_pod.m_double == 321.

        c = cppyy.gbl.CppyyTestData()
        c.set_pod_ptr_out(p)
        assert p.m_int == 888
        assert p.m_double == 3.14

        p.m_int = 555
        p.m_double = 666.

        c = cppyy.gbl.CppyyTestData()
        c.set_pod_ref(p)
        assert c.m_pod.m_int == 555
        assert c.m_pod.m_double == 666.

        c = cppyy.gbl.CppyyTestData()
        c.set_pod_ptrptr_in(p)
        assert c.m_pod.m_int == 555
        assert c.m_pod.m_double == 666.
        assert p.m_int == 555
        assert p.m_double == 666.

        c = cppyy.gbl.CppyyTestData()
        c.set_pod_void_ptrptr_in(p)
        assert c.m_pod.m_int == 555
        assert c.m_pod.m_double == 666.
        assert p.m_int == 555
        assert p.m_double == 666.

        c = cppyy.gbl.CppyyTestData()
        c.set_pod_ptrptr_out(p)
        assert c.m_pod.m_int == 888
        assert c.m_pod.m_double == 3.14
        assert p.m_int == 888
        assert p.m_double == 3.14

        p.m_int = 777
        p.m_double = 888.

        c = cppyy.gbl.CppyyTestData()
        c.set_pod_void_ptrptr_out(p)
        assert c.m_pod.m_int == 888
        assert c.m_pod.m_double == 3.14
        assert p.m_int == 888
        assert p.m_double == 3.14

    def test16_nullptr_passing(self):
        """Integer 0 ('NULL') and None allowed to pass through instance*"""

        import cppyy

        for o in (0, None):
            c = cppyy.gbl.CppyyTestData()
            assert c.m_pod.m_int == 888
            assert c.m_pod.m_double == 3.14
            assert not not c.m_ppod

            c.set_pod_ptr(o)
            assert not c.m_ppod
            assert not c.get_pod_ptr()

    def test17_respect_privacy(self):
        """Test that privacy settings are respected"""

        import cppyy
        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        assert isinstance(c, CppyyTestData)

        raises(AttributeError, getattr, c, 'm_owns_arrays')

        c.__destruct__()

    def test18_object_and_pointer_comparisons(self):
        """Object and pointer comparisons"""
    
        import cppyy 
        gbl = cppyy.gbl

        c1 = cppyy.bind_object(0, gbl.CppyyTestData)
        assert c1 == None
        assert None == c1

        c2 = cppyy.bind_object(0, gbl.CppyyTestData)
        assert c1 == c2
        assert c2 == c1

        # FourVector overrides operator==
        l1 = cppyy.bind_object(0, gbl.FourVector)
        assert l1 == None
        assert None == l1

        assert c1 != l1
        assert l1 != c1

        l2 = cppyy.bind_object(0, gbl.FourVector)
        assert l1 == l2
        assert l2 == l1

        l3 = gbl.FourVector(1, 2, 3, 4)
        l4 = gbl.FourVector(1, 2, 3, 4)
        l5 = gbl.FourVector(4, 3, 2, 1)
        assert l3 == l4
        assert l4 == l3

        assert l3 != None                 # like this to ensure __ne__ is called
        assert None != l3                 # id.
        assert l3 != l5
        assert l5 != l3

    def test19_object_validity(self):
        """Object validity checking"""
        
        from cppyy import gbl

        d = gbl.CppyyTestPod()
                     
        assert d
        assert not not d

        d2 = gbl.get_null_pod()

        assert not d2

    def test20_buffer_reshaping(self):
        """Usage of buffer (re)sizing"""

        import cppyy
        CppyyTestData = cppyy.gbl.CppyyTestData

        c = CppyyTestData()
        for func in ['get_bool_array',   'get_bool_array2',
                     'get_ushort_array', 'get_ushort_array2',
                     'get_int_array',    'get_int_array2',
                     'get_uint_array',   'get_uint_array2',
                     'get_long_array',   'get_long_array2',
                     'get_ulong_array',  'get_ulong_array2']:
            arr = getattr(c, func)()
            if not PYTEST_MIGRATION:
                arr = arr.shape.fromaddress(arr.itemaddress(0), self.N)
            if PYTEST_MIGRATION:
                arr.SetSize(self.N)
            assert len(arr) == self.N

            l = list(arr)
            for i in range(self.N):
                assert arr[i] == l[i]


## actual test run
if __name__ == '__main__':
    result = run_pytest(__file__)
    sys.exit(result)
