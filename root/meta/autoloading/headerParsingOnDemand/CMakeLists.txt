# We need to be able to specify the name of the library fully, no
# suffixes/prefixes automatically added, if we want compatibility
# with roottest. Indeed roottest does not allow
# dynamic rootmap creation: you have to commit one in the repository. If ctest
# creates another rootmap with the same keys but a different library name the
# system will complain at startup, making the test fail. Clearly for backwards
# compatibility reasons the current behaviour should be preserved :)

ROOTTEST_GENERATE_REFLEX_DICTIONARY(FullheaderParsingOnDemand FullheaderParsingOnDemand.h SELECTION FullheaderParsingOnDemand_selection.xml)

ROOTTEST_ADD_TEST(roottest-root-meta-autoloading-headerParsingOnDemand-runFullheaderParsingOnDemand
                  MACRO runFullheaderParsingOnDemand.C
                  OUTREF headerParsingOnDemand.ref
                  OUTCNV FullheaderParsingOnDemand_convert.sh
                  DEPENDS ${GENERATE_REFLEX_TEST})

ROOTTEST_GENERATE_REFLEX_DICTIONARY(complexTypedefs complexTypedefs.h SELECTION complexTypedefs_selection.xml)

ROOTTEST_ADD_TEST(roottest-root-meta-autoloading-headerParsingOnDemand-execCheckComplexTypedefs
                  MACRO execCheckComplexTypedefs.C
                  OUTREF execCheckComplexTypedefs.ref
                  DEPENDS ${GENERATE_REFLEX_TEST})
