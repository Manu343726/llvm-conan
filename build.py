from conan.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager()

    if platform.system() == "Linux":
        for ver in ["4.8", "4.9" "5.2", "5.3"]:
            for arch in ["x86", "x86_64"]:
                builder.add({"arch": arch,
                             "build_type": "Release",
                             "compiler": "gcc",
                             "compiler.version": ver},
                             {})
    builder.run()
