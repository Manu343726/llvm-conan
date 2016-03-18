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
