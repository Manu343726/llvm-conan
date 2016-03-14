PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

include(conanbuildinfo.cmake)

CONAN_BASIC_SETUP()

message (STATUS "${CMAKE_MODULE_PATH}")

include ("share/llvm/cmake/LLVMConfig")
include ("share/clang/cmake/ClangConfig")

IF(LLVM_INSTALL_PREFIX)
    include_directories(${LLVM_INCLUDE_DIRS}
                        ${CLANG_INCLUDE_DIRS})
    ADD_EXECUTABLE(executable "${CMAKE_CURRENT_SOURCE_DIR}/executable.cpp")
    TARGET_LINK_LIBRARIES(executable clangTooling)
ELSE()
    MESSAGE(FATAL_ERROR "ERROR! LLVM NOT FOUND!")
ENDIF()
