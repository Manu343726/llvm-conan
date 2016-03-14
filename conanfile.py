import sys

print(sys.path)

from contextlib import contextmanager
from conans import ConanFile, CMake
from conans.tools import download
import shutil
import os
import backports.lzma as lzma

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


def unlzma(lzma_name):
    import tarfile
    tar_name = os.path.splitext(lzma_name)[0]
    with lzma.open(lzma_name, "rb") as lzma_file:
        with open(tar_name, "wb") as tar_file:
            tar_file.write(lzma_file.read())

        with tarfile.open(tar_file.name, "r") as tar_file:
            tar_file.extractall(".")

        os.unlink(tar_file.name)


def extract_from_url(url):
    print("download {}".format(url))
    zip_name = os.path.basename(url)
    download(url, zip_name)
    unlzma(zip_name)
    os.unlink(zip_name)


def download_extract_llvm_component(component, release, extract_to):
    extract_from_url("http://llvm.org/releases/{ver}/{comp}-{ver}.src.tar.xz"
                     "".format(ver=release, comp=component))
    shutil.move("{comp}-{ver}.src".format(comp=component,
                                          ver=release),
                extract_to)


class LLVMConan(ConanFile):
    name = "llvm"
    version = os.environ.get("CONAN_VERSION_OVERRIDE", VERSION)
    generators = "cmake"
    requires = tuple()
    url = "http://github.com/smspillaz/llvm-conan"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        download_extract_llvm_component("llvm", LLVMConan.version, "src")
        download_extract_llvm_component("cfe", LLVMConan.version,
                                        "src/tools/clang")
        download_extract_llvm_component("compiler-rt", LLVMConan.version,
                                        "src/projects/compiler-rt")
        download_extract_llvm_component("libcxx", LLVMConan.version,
                                        "src/projects/libcxx")
        download_extract_llvm_component("libcxxabi", LLVMConan.version,
                                        "src/projects/libcxxabi")
        download_extract_llvm_component("libunwind", LLVMConan.version,
                                        "src/projects/libunwind")
        download_extract_llvm_component("clang-tools-extra", LLVMConan.version,
                                        "src/tools/clang/tools/extra")

    def build(self):
        cmake = CMake(self.settings)
        try:
            os.makedirs("install")
        except OSError:
            pass

        with in_dir("build"):
            self.run("cmake '{src}' {cmd}"
                     " -DBUILD_SHARED_LIBS=OFF"
                     " -DCMAKE_INSTALL_PREFIX={installdir}"
                     " -DCMAKE_VERBOSE_MAKEFILE=1"
                     "".format(src=os.path.join(self.conanfile_directory,
                                                "src"),
                               cmd=cmake.command_line,
                               installdir=os.path.join(os.getcwd(), "install")))
            self.run("cmake --build . {cfg}".format(cfg=cmake.build_config))
            self.run("cmake --build . -- install")

    def package(self):
        self.copy(pattern="*",
                  dst="include",
                  src="build/install/include",
                  keep_path=True)
        self.copy(pattern="*.a",
                  dst="lib",
                  src="build/install/lib",
                  keep_path=True)
        self.copy(pattern="*.h",
                  dst="lib",
                  src="build/install/lib",
                  keep_path=True)
        self.copy(pattern="*.so",
                  dst="lib",
                  src="build/install/lib",
                  keep_path=True)
        self.copy(pattern="*.dylib",
                  dst="lib",
                  src="build/install/lib",
                  keep_path=True)
        self.copy(pattern="*.lib",
                  dst="lib",
                  src="build/install/lib",
                  keep_path=True)
        self.copy(pattern="*.cmake",
                  dst="lib",
                  src="build/install/lib",
                  keep_path=True)
        self.copy(pattern="*.dll",
                  dst="lib",
                  src="build/install/lib",
                  keep_path=True)
        self.copy(pattern="*",
                  dst="share",
                  src="build/install/share",
                  keep_path=True)
        self.copy(pattern="*",
                  dst="bin",
                  src="build/install/bin",
                  keep_path=True)
        self.copy(pattern="*",
                  dst="libexec",
                  src="build/install/libexec",
                  keep_path=True)
