from conans import ConanFile, CMake, tools
import os


class OcilibConan(ConanFile):
    name = "ocilib"
    version = "4.9.0"
    license = "Apache-2.0"
    url = "git@github.com:dev-mylis/ocilib.git"
    description = "OCILIB C and C++ Oracle driver"
    topics = ("oracle", "oci", "database", "c", "cpp")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "oracle_import": ["runtime", "linkage"],
        "charset": ["ansi", "wide"],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "oracle_import": "runtime",
        "charset": "ansi",
    }
    generators = "cmake"
    exports_sources = ("CMakeLists.txt", "cmake/*", "src/**", "include/**", "LICENSE", "README.MD", "VERSION")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def build(self):
        cmake = CMake(self)
        args = [
            "-DBUILD_SHARED_LIBS={}".format("ON" if self.options.shared else "OFF"),
            "-DOCILIB_ORACLE_IMPORT={}".format(self.options.oracle_import),
            "-DOCILIB_CHARSET={}".format(self.options.charset),
        ]

        if self.options.oracle_import == "linkage":
            oracle_home = os.getenv("ORACLE_HOME", "")
            oci_include = os.getenv("OCI_INCLUDE_DIR", "")
            oci_lib = os.getenv("OCI_LIBRARY_DIR", "")
            if not oci_include and oracle_home:
                oci_include = os.path.join(oracle_home, "rdbms", "public")
            if not oci_lib and oracle_home:
                oci_lib = os.path.join(oracle_home, "lib")
            if oci_include:
                args.append("-DOCI_INCLUDE_DIR={}".format(oci_include))
            if oci_lib:
                args.append("-DOCI_LIBRARY_DIR={}".format(oci_lib))

        cmake.configure(source_folder=self.source_folder, args=args)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ocilib"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread", "dl"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.builddirs = ["lib/cmake/ocilib"]
        self.cpp_info.defines = [
            "OCI_IMPORT_RUNTIME" if self.options.oracle_import == "runtime"
            else "OCI_IMPORT_LINKAGE",
            "OCI_CHARSET_ANSI" if self.options.charset == "ansi"
            else "OCI_CHARSET_WIDE",
        ]
