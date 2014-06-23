#-------------------------------------------------------------------------------
#
# RootCTestMacros.cmake
#
# Macros for adding tests to CTest.
#
#-------------------------------------------------------------------------------

include(RootMacros)

macro(ROOTTEST_SETUP_MACROTEST)

  get_directory_property(DirDefs COMPILE_DEFINITIONS)

  foreach(d ${DirDefs})
    list(APPEND RootExeDefines "-e;#define ${d}")
  endforeach()

  set(root_cmd root.exe ${RootExeDefines}
               -e "gSystem->SetBuildDir(\"${CMAKE_CURRENT_BINARY_DIR}\",true)"
               -e "gSystem->AddDynamicPath(\"${CMAKE_CURRENT_BINARY_DIR}\")"
               -e "gROOT->SetMacroPath(\"${CMAKE_CURRENT_SOURCE_DIR}\")"
               -e "gSystem->AddIncludePath(\"-I${CMAKE_CURRENT_BINARY_DIR}\")"
               -q -l -b) 

  set(root_buildcmd root.exe ${RootExeDefines} -q -l -b)

  # Compile macro, then add to CTest.
  if(ARG_MACRO MATCHES "[.]C\\+" OR ARG_MACRO MATCHES "[.]cxx\\+")
    string(REPLACE "+" "" compile_name "${ARG_MACRO}")
    get_filename_component(realfp ${compile_name} REALPATH)

    ROOTTEST_COMPILE_MACRO(${compile_name})

    set(depends ${depends} ${COMPILE_MACRO_TEST})

    if(DEFINED ARG_MACROARG)
      set(realfp "${realfp}(${ARG_MACROARG})") 
    endif()

    set(command ${root_cmd} "${realfp}+")

  # Add interpreted macro to CTest.
  elseif(ARG_MACRO MATCHES "[.]C" OR ARG_MACRO MATCHES "[.]cxx")
    get_filename_component(realfp ${ARG_MACRO} REALPATH)
    if(DEFINED ARG_MACROARG)
      set(realfp "${realf}(${ARG_MACROARG})") 
    endif()

    set(command ${root_cmd} ${realfp})
    
  # Add python script to CTest.
  elseif(ARG_MACRO MATCHES "[.]py")
    get_filename_component(realfp ${ARG_MACRO} REALPATH)
    set(command ${python_cmd} ${realfp})

  elseif(DEFINED ARG_MACRO)
    set(command ${root_cmd} ${ARG_MACRO})
  endif()

  # Check for assert prefix -- only log stderr.
  if(ARG_MACRO MATCHES "^assert")
    set(checkstdout "")
    set(checkstderr CHECKERR)
  else()
    set(checkstdout CHECKOUT)
    set(checkstderr CHECKERR)
  endif()

endmacro(ROOTTEST_SETUP_MACROTEST)

macro(ROOTTEST_SETUP_EXECTEST)

  find_program(realexec ${ARG_EXEC}
               HINTS $ENV{PATH}
               PATH ${CMAKE_CURRENT_BINARY_DIR}
               PATH ${CMAKE_CURRENT_SOURCE_DIR})

  # If no program was found, take it as is.
  if(NOT realexec)
    set(realexec ${ARG_EXEC})
  endif()

  set(command ${realexec})

  set(checkstdout CHECKOUT)
  set(checkstderr CHECKERR)

endmacro(ROOTTEST_SETUP_EXECTEST)

function(ROOTTEST_ADD_TEST test)
  CMAKE_PARSE_ARGUMENTS(ARG "WILLFAIL;TEST_OUTREF_CINTSPECIFIC"
                            "OUTREF;OUTCNV;PASSRC;MACROARG;WORKING_DIR"
                            "TESTOWNER;COPY_TO_BUILDDIR;MACRO;EXEC;PRECMD;POSTCMD;OUTCNVCMD;FAILREGEX;PASSREGEX;DEPENDS;OPTS;LABELS" ${ARGN})

  # Setup macro test.
  if(ARG_MACRO)
   ROOTTEST_SETUP_MACROTEST()
  endif()

  # Setup executable test.
  if(ARG_EXEC)
    ROOTTEST_SETUP_EXECTEST()
  endif()

  # Reference output given?
  if(ARG_OUTREF)
    get_filename_component(OUTREF_PATH ${ARG_OUTREF} ABSOLUTE)

    if(DEFINED X86_64)
      set(ROOTBITS 64)
    elseif(DEFINED X86)
      set(ROOTBITS 32)
    else()
      set(ROOTBITS "")
    endif()

    if(ARG_TEST_OUTREF_CINTSPECIFIC)
      if(EXISTS ${OUTREF_PATH}${ROOTBITS}-${CINT_VERSION})
        set(OUTREF_PATH ${OUTREF_PATH}${ROOTBITS}-${CINT_VERSION})
      elseif(EXISTS ${OUTREF_PATH}-${CINT_VERSION})
        set(OUTREF_PATH ${OUTREF_PATH}-${CINT_VERSION})
      elseif(EXISTS ${OUTREF_PATH}${ROOTBITS})
        set(OUTREF_PATH ${OUTREF_PATH}${ROOTBITS})
      endif() 
    else()
      if(EXISTS ${OUTREF_PATH}${ROOTBITS})
        set(OUTREF_PATH ${OUTREF_PATH}${ROOTBITS})
      endif()
    endif()

  else()
    set(OUTREF_PATH "")
  endif()

  if(ARG_OUTCNV)
    get_filename_component(OUTCNV ${ARG_OUTCNV} ABSOLUTE)
  endif()

  # Get the real path to the output conversion script.
  if(ARG_OUTCNV)
    get_filename_component(OUTCNV ${ARG_OUTCNV} ABSOLUTE)
    set(outcnv OUTCNV ${OUTCNV})
  endif()

  # Setup the output conversion command.
  if(ARG_OUTCNVCMD)
    set(outcnvcmd OUTCNVCMD ${ARG_OUTCNVCMD})
  endif()

  # Mark the test as known to fail.
  if(ARG_WILLFAIL)
    set(willfail WILLFAIL)
  endif()

  # Add ownership and test labels.
  get_property(testowner DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                         PROPERTY ROOTTEST_TEST_OWNER)

  if(ARG_TESTOWNER)
    set(testowner ${ARG_TESTOWNER})
  endif()

  if(ARG_LABELS)
    set(labels LABELS ${ARG_LABELS})
    if(testowner)
      set(labels ${labels} ${testowner}) 
    endif()
  else()
    if(testowner)
      set(labels LABELS ${testowner}) 
    endif()
  endif()

  # Test will pass for a custom return value.
  if(ARG_PASSRC)
    set(passrc PASSRC ${ARG_PASSRC})
  endif()

  # Pass options to the command.
  if(ARG_OPTS)
    set(command ${command} ${ARG_OPTS})
  endif()

  # Execute a custom command before executing the test.
  if(ARG_PRECMD)
    set(precmd PRECMD ${ARG_PRECMD})
  endif()

  # Copy files into the build directory first.
  if(ARG_COPY_TO_BUILDDIR)
    foreach(copyfile ${ARG_COPY_TO_BUILDDIR})
      get_filename_component(absfilep ${copyfile} ABSOLUTE)
      set(copy_files ${copy_files} ${absfilep})
    endforeach()
    set(copy_to_builddir COPY_TO_BUILDDIR ${copy_files})
  endif()

  # Execute a custom command after executing the test.
  if(ARG_POSTCMD)
    set(postcmd POSTCMD ${ARG_PRECMD})
  endif()

  # Add dependencies. If the test depends on a macro file, the macro
  # will be compiled and the dependencies are set accordingly.
  if(ARG_DEPENDS)
    foreach(dep ${ARG_DEPENDS})
      list(APPEND deplist ${dep})

      if(${dep} MATCHES "[.]C" OR ${dep} MATCHES "[.]cxx" OR ${dep} MATCHES "[.]h")
        ROOTTEST_COMPILE_MACRO(${dep})

        set(depends ${depends} ${COMPILE_MACRO_TEST})
        
        list(REMOVE_ITEM deplist ${dep})
      endif()
    endforeach()
    set(depends ${depends} ${deplist})
  endif(ARG_DEPENDS)

  if(ARG_FAILREGEX)
    set(failregex FAILREGEX ${ARG_FAILREGEX})
  endif()

  if(ARG_PASSREGEX)
    set(passregex PASSREGEX ${ARG_PASSREGEX})
  endif()

  string(REPLACE ";" ":" _path "${ROOTTEST_ENV_PATH}")
  string(REPLACE ";" ":" _pythonpath "${ROOTTEST_ENV_PYTHONPATH}")
  string(REPLACE ";" ":" _librarypath "${ROOTTEST_ENV_LIBRARYPATH}")

  set(environment ENVIRONMENT
                  ROOTSYS=${ROOTSYS}
                  PATH=${_path}:$ENV{PATH}
                  PYTHONPATH=${_pythonpath}:$ENV{PYTHONPATH}
                  ${ld_library_path}=${_librarypath}:$ENV{${ld_library_path}} )

  if(ARG_WORKING_DIR)
    get_filename_component(test_working_dir ${ARG_WORKING_DIR} ABSOLUTE)
  else()
    get_filename_component(test_working_dir ${CMAKE_CURRENT_BINARY_DIR} ABSOLUTE)
  endif()

  get_filename_component(logdir "${CMAKE_CURRENT_BINARY_DIR}/${test}.log" ABSOLUTE)

  ROOT_ADD_TEST(${test} COMMAND ${command}
                        OUTPUT ${logdir}
                        ${outcnv}
                        ${outcnvcmd}
                        CMPOUTPUT ${OUTREF_PATH}
                        WORKING_DIR ${test_working_dir}
                        DIFFCMD sh ${ROOTTEST_DIR}/scripts/custom_diff.sh
                        TIMEOUT 3600
                        ${environment}
                        ${build}
                        ${checkstdout}
                        ${checkstderr}
                        ${willfail}
                        ${compile_macros}
                        ${labels}
                        ${passrc}
                        ${precmd}
                        ${postcmd}
                        ${failregex}
                        ${passregex}
                        ${copy_to_builddir}
                        DEPENDS ${depends})

endfunction(ROOTTEST_ADD_TEST)
