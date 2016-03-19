from contextlib import contextmanager
from conans import ConanFile, CMake
from conans.tools import download, unzip
import shutil
import os
import platform

VERSION = "3.8.0"


@contextmanager
def in_dir(directory):
    last_dir = os.getcwd()
    try:
        os.makedirs(directory)
    except OSError:
        pass

    try:
        os.chdir(directory)
        yield directory
    finally:
        os.chdir(last_dir)


def extract_from_url(url):
    print("download {}".format(url))
    zip_name = os.path.basename(url)
    download(url, zip_name)
    unzip(zip_name)
    os.unlink(zip_name)


def download_extract_llvm_component(component, release, extract_to):
    extract_from_url("https://bintray.com/artifact/download/"
                     "polysquare/LLVM/{comp}-{ver}.src.zip"
                     "".format(ver=release, comp=component))
    shutil.move("{comp}-{ver}.src".format(comp=component,
                                          ver=release),
                extract_to)


BUILD_DIR = ("C:/__build" if platform.system == "Windows"
             else "build")
INSTALL_DIR = "install"  # This needs to be a relative path

class LLVMConan(ConanFile):
    name = "llvm"
    version = os.environ.get("CONAN_VERSION_OVERRIDE", VERSION)
    generators = "cmake"
    requires = tuple()
    url = "http://github.com/smspillaz/llvm-conan"
    license = "BSD"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"

    def config(self):
        try:  # Try catch can be removed when conan 0.8 is released
            del self.settings.compiler.libcxx
        except:
            pass

    def source(self):
        download_extract_llvm_component("llvm", LLVMConan.version, "src")

    def build(self):
        cmake = CMake(self.settings)
        try:
            os.makedirs(INSTALL_DIR)
        except OSError:
            pass

        try:
            shutil.rmtree(BUILD_DIR)
        except OSError:
            pass

        with in_dir(BUILD_DIR):
            self.run("cmake \"%s\" %s"
                     " -DCLANG_INCLUDE_DOCS=OFF"
                     " -DCLANG_INCLUDE_TESTS=OFF"
                     " -DCLANG_TOOLS_INCLUDE_EXTRA_DOCS=OFF"
                     " -DCOMPILER_RT_INCLUDE_TESTS=OFF"
                     " -DLIBCXX_INCLUDE_TESTS=OFF"
                     " -DLIBCXX_INCLUDE_DOCS=OFF"
                     " -DLLVM_INCLUDE_TESTS=OFF"
                     " -DLLVM_INCLUDE_TOOLS=ON"
                     " -DLLVM_BUILD_TOOLS=ON"
                     " -DLLVM_TOOL_LLVM_AR_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_AS_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_AS_FUZZER_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_BUGPOINT_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_BUGPOINT_PASSES_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_BCANALYZER_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_COV_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_CXXDUMP_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_DSYMUTIL_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_LLC_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_LLI_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_DWARFDUMP_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_DIS_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_EXTRACT_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_C_TEST_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_DIFF_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_GO_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_JITLISTENER_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_LTO_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_MCMARKUP_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_MC_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_MC_FUZZER_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_NM_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_OBJDUMP_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_BCANALYZER_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_PDBDUMP_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_PROFDATA_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_RTDYLD_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_SIZE_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_SPLIT_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_STRESS_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_SYMBOLIZER_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_LTO_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_OBJ2YAML_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_OPT_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_SANCOV_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_SANSTATS_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_VERIFY_USELISTORDER_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_XCODE_TOOLCHAIN_BUILD=OFF"
                     " -DLLVM_TOOL_LLVM_YAML2OBJ_BUILD=OFF"
                     " -DLLVM_INCLUDE_EXAMPLES=OFF"
                     " -DLLVM_INCLUDE_GO_TESTS=OFF"
                     " -DLLVM_BUILD_TESTS=OFF"
                     " -DCMAKE_VERBOSE_MAKEFILE=1"
                     " -DLLVM_TARGETS_TO_BUILD=X86"
                     " -DCMAKE_INSTALL_PREFIX=\"%s\""
                     " -DBUILD_SHARED_LIBS=%s"
                     "" % (os.path.join(self.conanfile_directory,
                                        "src"),
                           cmake.command_line,
                           os.path.join(self.conanfile_directory,
                                        INSTALL_DIR),
                           ("ON" if self.options.shared else "OFF")))
            self.run("cmake --build . {cfg} -- {j}"
                     "".format(cfg=cmake.build_config,
                               j=("-j4" if platform.system() != "Windows"
                                  else "")))
            self.run("cmake --build . -- install")

    def package(self):
        self.copy(pattern="*",
                  dst="include",
                  src=os.path.join(INSTALL_DIR, "include"),
                  keep_path=True)
        for pattern in ["*.a", "*.h", "*.so", "*.lib", "*.dylib", "*.dll", "*.cmake"]:
            self.copy(pattern=pattern,
                      dst="lib",
                      src=os.path.join(INSTALL_DIR, "lib"),
                      keep_path=True)
        self.copy(pattern="*",
                  dst="share",
                  src=os.path.join(INSTALL_DIR, "share"),
                  keep_path=True)
        self.copy(pattern="*",
                  dst="bin",
                  src=os.path.join(INSTALL_DIR, "bin"),
                  keep_path=True)
        self.copy(pattern="*",
                  dst="libexec",
                  src=os.path.join(INSTALL_DIR, "libexec"),
                  keep_path=True)
