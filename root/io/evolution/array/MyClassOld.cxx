#define MYCLASS 2
#include "MyClass.cxx"

#ifdef __MAKECINT__
// to be included only if coompiling the new version of the class
#pragma read sourceClass="MyClass" targetClass="MyClass" \
source="Int_t farray" version="[1]" target="fentries, farrayPointer" targetType="Int_t*, Int_t"\
code="{fentries = 5; farrayPointer = new Int_t[fentries]; memcpy(farrayPointer, &(onfile.farray), fentries*sizeof(Int_t)); }"
#endif