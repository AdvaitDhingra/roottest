all: tests

test: tests ;

# The previous line contains just ';' in order to disable the implicit 
# rule building an executable 'test' from test.C

# The user directory should define
# SUBDIRS listing any activated subdirectory
# TEST_TARGETS with the list of activated test
# CLEAN_TARGETS with the list of things to delete

# doing gmake VERBOSE=true allows for more output, include the original
# commands.

# doing gmake FAIL=true run the test that are known to fail

SUBDIRS = $(shell $(ROOTTEST_HOME)scripts/subdirectories .)

TEST_TARGETS_DIR = $(SUBDIRS:%=%.test) 
TEST_TARGETS += $(TEST_TARGETS_DIR)

CLEAN_TARGETS_DIR = $(SUBDIRS:%=%.clean)
CLEAN_TARGETS += 

ALL_LIBRARIES += *.d *.o *.so *.def *.exp *.dll *.lib dummy.C *.pdb .def

export CURDIR=$(shell basename `pwd`)
#debug:=$(shell echo CALLDIR=$(CALLDIR) CURDIR=$(CURDIR) PWD=`pwd` 1>&2 ) 
ifeq ($(CALLDIR),)
	export CALLDIR:=.
else
	export CALLDIR:=$(CALLDIR)/$(CURDIR)
endif

tests: $(TEST_TARGETS)
	@echo "All test succeeded in $(CALLDIR)"

$(TEST_TARGETS_DIR): %.test:
	@(echo Running test in $(CALLDIR)/$*)
	@(cd $*; gmake --no-print-directory test)

$(CLEAN_TARGETS_DIR): %.clean:
	@(cd $*; gmake --no-print-directory clean)

ifneq ($(V),) 
VERBOSE:=$(V)
endif
ifeq ($(VERBOSE),) 
   CMDECHO=@
else
   CMDECHO=
endif

clean:  $(CLEAN_TARGETS_DIR)
	$(CMDECHO) rm -f main *Dict\.* Event.root *~ $(CLEAN_TARGETS)


# here we guess the platform

ARCH          = $(shell root-config --arch)
PLATFORM      = $(ARCH)

CXXFLAGS = $(shell root-config --cflags)
ROOTLIBS     := $(shell root-config --nonew --libs)
ROOTGLIBS    := $(shell root-config --nonew --glibs)

ObjSuf   = o

ifeq ($(PLATFORM),win32)
# Windows with the VC++ compiler
ObjSuf        = obj
SrcSuf        = cxx
ExeSuf        = .exe
DllSuf        = dll
OutPutOpt     = -out:
CXX           = cl
CXXOPT        = -O2
#CXXOPT        = -Z7
#CXXFLAGS      = $(CXXOPT) -G5 -GR -MD -DWIN32 -D_WINDOWS -nologo \
#                -DVISUAL_CPLUSPLUS -D_X86_=1 -D_DLL
CXXFLAGS      += /TP /GX  -G5 -GR
LD            = link
#LDOPT         = -opt:ref
#LDOPT         = -debug
#LDFLAGS       = $(LDOPT) -nologo -nodefaultlib -incremental:no
SOFLAGS       = -DLL
SYSLIBS       = msvcrt.lib oldnames.lib kernel32.lib  ws2_32.lib mswsock.lib \
                advapi32.lib  user32.lib gdi32.lib comdlg32.lib winspool.lib 

#                msvcirt.lib

endif

ifeq ($(ARCH),linux)
# Linux with egcs, gcc 2.9x, gcc 3.x (>= RedHat 5.2)
CXX           = g++
ifeq ($(ROOTBUILD),debug)
CXXFLAGS      += -g -Wall -fPIC
else
CXXFLAGS      += -O -Wall -fPIC
endif
LD            = g++
ifeq ($(ROOTBUILD),debug)
LDFLAGS       = -g 
else
LDFLAGS       = -O
endif
SOFLAGS       = -shared
ObjSuf        = o
SrcSuf        = cxx
ExeSuf        =
DllSuf        = so
OutPutOpt     = -o 
endif

ifeq ($(ARCH),linuxicc)
# Linux with linuxicc
CXX = icc
LD  = icc
ifeq ($(ROOTBUILD),debug)
CXXFLAGS += -g -wd191 
else
CXXFLAGS += -O -wd191 
endif
SOFLAGS  = -shared 
DllSuf   = so
ExeSuf   = 
OutPutOpt= -o 
endif

.SUFFIXES: .$(SrcSuf) .$(ObjSuf) .$(DllSuf) .$(ExeSuf)

##### utilities #####

ifeq ($(PLATFORM),win32)
MAKELIB       = $(ROOTTEST_HOME)/scripts/winmakelib.sh
else
MAKELIB       = $(ROOTSYS)/build/unix/makelib.sh $(MKLIBOPTIONS)
endif

%.o: %.C
	$(CMDECHO) $(CXX) $(CXXFLAGS) -c $< > $*_o_C.build.log 2>&1

%.o: %.cxx
	$(CMDECHO) $(CXX) $(CXXFLAGS) -c $< > $*_o_cxx.build.log 2>&1

%.o: %.cpp
	$(CMDECHO) $(CXX) $(CXXFLAGS) -c $< > $*_o_cpp.build.log 2>&1

%.obj: %.C
	$(CMDECHO) $(CXX) $(CXXFLAGS) -c $< > $*_obj_C.build.log 2>&1

%.obj: %.cxx
	$(CMDECHO) $(CXX) $(CXXFLAGS) -c $< > $*_obj_cxx.build.log 2>&1

%.obj: %.cpp
	$(CMDECHO) $(CXX) $(CXXFLAGS) -c $< > $*_obj_cpp.build.log 2>&1
	
%_cpp.$(DllSuf) : %.cpp
	$(CMDECHO) root.exe -q -l -b $(ROOTTEST_HOME)/scripts/build.C\(\"$<\"\) > $*_cpp.build.log 2>&1

%_C.$(DllSuf) : %.C
	$(CMDECHO) root.exe -q -l -b $(ROOTTEST_HOME)/scripts/build.C\(\"$<\"\) > $*_C.build.log 2>&1

%_cxx.$(DllSuf) : %.cxx
	$(CMDECHO) root.exe -q -l -b $(ROOTTEST_HOME)/scripts/build.C\(\"$<\"\) > $*_cxx.build.log 2>&1

%_h.$(DllSuf) : %.h
	$(CMDECHO) root.exe -q -l -b $(ROOTTEST_HOME)/scripts/build.C\(\"$<\"\) > $*_h.build.log 2>&1

%.log : run%.C
	$(CMDECHO) root.exe -q -l -b $< > $@ 2>&1

define BuildWithLib
	$(CMDECHO) root.exe -q -l -b $(ROOTTEST_HOME)/scripts/build.C\(\"$<\"\,\"$(filter %.$(DllSuf),$^)\"\) > $*.build.log 2>&1
endef
    
define WarnFailTest
	$(CMDECHO)echo Warning $@ has some known skipped failures "(in ./$(CURDIR))"
endef

define TestDiff
	$(CMDECHO) diff -b $@.ref $<
endef

define BuildFromObj
$(CMDECHO) touch dummy.C
$(CMDECHO) root.exe -q -l -b $(ROOTTEST_HOME)/scripts/build.C\(\"dummy.C\"\,\"$<\",1\) > $@.build.log 2>&1
$(CMDECHO) mv dummy_C.$(DllSuf) $@ 
endef

define BuildFromObjs
$(CMDECHO) touch dummy.C
$(CMDECHO) root.exe -q -l -b "$(ROOTTEST_HOME)/scripts/build.C(\"dummy.C\",\"$^\",1)" > $@.build.log 2>&1
$(CMDECHO) mv dummy_C.$(DllSuf) $@ 
endef

RemoveLeadingDirs := sed -e 's?^[A-z/\].*[/\]??' -e 's/.dll/.so/'
RemoveDirs := sed -e 's?([A-z]:|[/]).*[/\]??'


