"""The checks module contains two classes that are used to verify
conda packages and recipes: CondaPackageCheck and CondaRecipeCheck.

Each class contains specific checks that relate to validating packages
and recipes. These checks start with the letter 'C', which is an
abbreviation for 'conda'.

Checks C1101 through C1148 are housed in CondaPackageCheck.
Checks C2101 through C2126 are housed in CondaRecipeCheck.
"""
import hashlib
import json
import os
import re
import sys

import conda_package_handling.api

try:
    from tempfile import TemporaryDirectory
except:
    from backports.tempfile import TemporaryDirectory

from conda_verify.errors import Error, PackageError
from conda_verify.constants import FIELDS, LICENSE_FAMILIES, CONDA_FORGE_COMMENTS
from conda_verify.utilities import (
    all_ascii,
    get_bad_seq,
    get_object_type,
    ensure_list,
    fullmatch,
    rm_rf,
)


ver_spec_pat = r"^(?:[><=]{0,2}(?:(?:[\d\*]+[!\._]?){1,})[+\w\*]*[|,]?){1,}"


def _checksum(fd, algorithm, buffersize=65536):
    hash_impl = getattr(hashlib, algorithm)
    if not hash_impl:
        raise ValueError("Unrecognized hash algorithm: {}".format(algorithm))
    else:
        hash_impl = hash_impl()
    for block in iter(lambda: fd.read(buffersize), b""):
        hash_impl.update(block)
    return hash_impl.hexdigest()


def sha256_checksum(fd):
    return _checksum(fd, "sha256")


class CondaPackageCheck(object):
    """Create checks in order to validate conda package tarballs."""

    def __init__(self, path):
        """Initialize conda package information for use with package checks."""
        super(CondaPackageCheck, self).__init__()
        self.path = path
        self.dist = self.retrieve_package_name(self.path)

        self._tmpdir = TemporaryDirectory()
        self.tmpdir = self._tmpdir.name
        conda_package_handling.api.extract(self.path, self.tmpdir)
        self.name, self.version, self.build = self.dist.rsplit("-", 2)
        self.paths = self.archive_members = [
            os.path.relpath(os.path.join(dp, f), self.tmpdir)
            for dp, dn, filenames in os.walk(self.tmpdir)
            for f in filenames
        ]
        with open(os.path.join(self.tmpdir, "info", "index.json"), "rb") as f:
            self.index = f.read()
        self.info = json.loads(self.index.decode("utf-8"))

        with open(os.path.join(self.tmpdir, "info", "files"), "rb") as f:
            self.files_file = f.read()

        try:
            with open(os.path.join(self.tmpdir, "info", "has_prefix"), "rb") as f:
                self.prefix_file = f.read()
        except IOError:
            self.prefix_file = None

        self.paths_json_path = dict()
        try:
            with open(os.path.join(self.tmpdir, 'info', 'paths.json')) as f:
                self.paths_json = json.load(f)
                for path in self.paths_json['paths']:
                    self.paths_json_path[path["_path"]] = path
        except IOError:
            assert self.info.subdir == 'noarch'
            self.paths_json = {}

        self.win_pkg = bool(self.info["platform"] == "win")
        self.name_pat = re.compile(r"[a-z0-9_][a-z0-9_\-\.]*$")
        self.hash_pat = re.compile(r"[gh][0-9a-f]{5,}", re.I)
        self.version_pat = re.compile(r"[\w\.]+$")

    def __exit__(self, exc, value, tb):
        rm_rf(self._tmpdir.name)

    @staticmethod
    def retrieve_package_name(path):
        """Retrieve the package name from the conda package path."""
        path = os.path.basename(path)
        seq = get_bad_seq(path)
        if seq:
            raise PackageError(
                u'Found invalid sequence "{}" in package in info/index.json'.format(seq)
            )

        if path.endswith(".tar.bz2"):
            return path[:-8]
        elif path.endswith(".tar"):
            return path[:-4]
        elif path.endswith(".conda"):
            return path[:-6]
        else:
            raise PackageError(
                'Found package with invalid extension "{}"'.format(
                    os.path.splitext(path)[1]
                )
            )

    def check_package_name(self):
        """Check the package name located in info/index.json."""
        package_name = self.info.get("name")
        if package_name is None:
            return Error(self.path, "C1101", "Missing package name in info/index.json")

        if not self.name_pat.match(package_name) or package_name.endswith(
            (".", "-", "_")
        ):
            return Error(
                self.path, "C1103", "Found invalid package name in info/index.json"
            )

        if package_name != self.name:
            return Error(
                self.path,
                "C1102",
                u'Found package name in info/index.json "{}" does not match filename "{}"'.format(
                    package_name, self.name
                ),
            )

    def check_package_version(self):
        """Check the package version located in info/index.json."""
        package_version = str(self.info.get("version"))
        if package_version == "None":
            return Error(
                self.path, "C1104", "Missing package version in info/index.json"
            )
        if package_version.startswith(("_", ".")) or package_version.endswith(
            ("_", ".")
        ):
            return Error(
                self.path,
                "C1107",
                "Package version in info/index.json cannot start or end with '_' or '.'",
            )
        if not self.version_pat.match(package_version) or get_bad_seq(package_version):
            return Error(
                self.path, "C1105", "Found invalid version number in info/index.json"
            )
        if package_version != self.version:
            return Error(
                self.path,
                "C1106",
                u'Found package version in info/index.json "{}" does not match filename version "{}"'.format(
                    package_version, self.version
                ),
            )

    def check_build_number(self):
        """Check the build number located in info/index.json."""
        build_number = self.info.get("build_number")
        if build_number is not None:
            try:
                build_number = int(build_number)
                if build_number < 0:
                    return Error(
                        self.path,
                        "C1109",
                        "Build number in info/index.json cannot be a negative integer",
                    )

            except ValueError:
                return Error(
                    self.path,
                    "C1108",
                    "Build number in info/index.json must be an integer",
                )

    def check_build_string(self):
        """Check the build string in info/index.json."""
        build_string = self.info.get("build")
        if not self.version_pat.match(build_string):
            return Error(
                self.path,
                "C1110",
                'Found invalid build string "{}" in info/index.json'.format(
                    build_string
                ),
            )
        if build_string != self.build:
            return Error(
                self.path,
                "C1111",
                'Found build number in info/index.json "{}" does not match build number "{}" in filename'.format(
                    build_string, self.build
                ),
            )

    def check_index_dependencies(self):
        """Check that the dependencies field is present in info/index.json."""
        depends = self.info.get("depends")
        if depends is None:
            return Error(
                self.path, "C1112", 'Missing "depends" field in info/index.json'
            )

    def check_index_dependencies_specs(self):
        """Check that the dependencies in info/index.json are properly formatted."""
        dependencies = ensure_list(self.info.get("depends"))
        if dependencies != [None]:
            for dependency in dependencies:
                dependency_parts = dependency.split()
                if len(dependency_parts) == 0:
                    return Error(
                        self.path,
                        "C1113",
                        "Found empty dependencies in info/index.json",
                    )
                elif (
                    len(dependency_parts) == 2
                    and not fullmatch(ver_spec_pat, dependency_parts[1])
                    or len(dependency_parts) > 3
                ):
                    return Error(
                        self.path,
                        "C1114",
                        'Found invalid dependency "{}" in info/index.json'.format(
                            dependency
                        ),
                    )

    def check_license_family(self):
        """Check that the license family in info/index.json is valid."""
        license = self.info.get("license_family", self.info.get("license"))
        if license not in LICENSE_FAMILIES:
            return Error(
                self.path,
                "C1115",
                'Found invalid license "{}" in info/index.json'.format(license),
            )

    def check_index_encoding(self):
        """Check that contents of info/index.json are all ascii characters."""
        if not all_ascii(self.index, self.win_pkg):
            return Error(
                self.path, "C1116", "Found non-ascii characters inside info/index.json"
            )

    def check_members(self):
        """Check the tar archive members for non ascii characters."""
        for member in self.archive_members:
            if sys.version_info.major == 2:
                unicode_path = member.decode("utf-8")
            else:
                unicode_path = member.encode("utf-8")

            if not all_ascii(unicode_path):
                return Error(
                    self.path,
                    "C1118",
                    "Found archive member names containing non-ascii characters",
                )

    def check_files_file_encoding(self):
        """Check the info/files file for non ascii characters."""
        if not all_ascii(self.files_file, self.win_pkg):
            return Error(
                self.path,
                "C1119",
                "Found filenames in info/files containing non-ascii characters",
            )

    def check_files_file_for_info(self):
        """Check that the info/files file does not contain any files found within the info directory."""
        filenames = [
            path.strip() for path in self.files_file.decode("utf-8").splitlines()
        ]
        for filename in filenames:
            if filename.startswith("info"):
                return Error(
                    self.path,
                    "C1120",
                    'Found filenames in info/files that start with "info"',
                )

    def check_files_file_for_duplicates(self):
        """Check the info/files file for duplicates."""
        filenames = [
            path.strip() for path in self.files_file.decode("utf-8").splitlines()
        ]
        if len(filenames) != len(set(filenames)):
            return Error(self.path, "C1121", "Found duplicate filenames in info/files")

    def check_files_file_for_validity(self):
        """Check that the files listed in info/files exist in the tar archive and vice versa."""
        members = set([
            member
            for member in self.archive_members
            if not os.path.isdir(os.path.join(self.tmpdir, member))
            and not member.startswith("info")
        ])
        filenames = set([
            os.path.normpath(path.strip())
            for path in self.files_file.decode("utf-8").splitlines()
            if not path.strip().startswith("info")
        ])

        sorted_union_filenames = sorted(members.union(filenames))
        for filename in sorted_union_filenames:
            if filename not in members:
                return Error(
                    self.path,
                    "C1122",
                    (
                        u"Found filename in info/files missing from tar " "archive: {}"
                    ).format(filename),
                )
            elif filename not in filenames:
                return Error(
                    self.path,
                    "C1123",
                    u"Found filename in tar archive missing from info/files: {}".format(
                        filename
                    ),
                )

    def check_for_hardlinks(self):
        """Check the tar archive for hardlinks."""
        for member in self.archive_members:
            if os.path.islink(os.path.join(self.tmpdir, member)):
                return Error(
                    self.path,
                    "C1124",
                    u"Found hardlink {} in tar archive".format(member),
                )

    def check_for_unallowed_files(self):
        """Check the tar archive for unallowed directories."""
        unallowed_directories = {"conda-meta", "conda-bld", "pkgs", "pkgs32", "envs"}

        for filepath in self.paths:
            if filepath in unallowed_directories or filepath.endswith(
                (".DS_Store", "~")
            ):
                return Error(
                    self.path,
                    "C1125",
                    u"Found unallowed file in tar archive: {}".format(filepath),
                )

    def check_for_noarch_info(self):
        """Check that noarch Python packages contain the proper metadata files."""
        for filepath in self.paths:
            if filepath in (
                os.path.join("info", "package_metadata.json"),
                os.path.join("info", "link.json"),
            ):
                if self.info["subdir"] != "noarch" and "preferred_env" not in self.info:
                    return Error(
                        self.path,
                        "C1126",
                        u"Found {} however package is not a noarch package".format(
                            filepath
                        ),
                    )

    def check_for_bat_and_exe(self):
        """Check that both .bat and .exe files don't exist in the same package."""
        bat_files = [
            filepath[:-4] for filepath in self.paths if filepath.endswith(".bat")
        ]
        exe_files = [
            filepath[:-4] for filepath in self.paths if filepath.endswith(".exe")
        ]

        isect = set(bat_files).intersection(exe_files)
        if len(isect) > 0:
            return Error(
                self.path,
                "C1127",
                "Found both .bat and .exe files with same basename in same folder: {}".format(
                    isect
                ),
            )

    def check_prefix_file(self):
        """Check the info/has_prefix file for proper formatting."""
        if self.prefix_file is not None:
            if not all_ascii(self.prefix_file, self.win_pkg):
                return Error(
                    self.path, "C1128", "Found non-ascii characters in info/has_prefix"
                )

    @property
    def prefix_file_contents(self):
        """Extract the contents of the has_prefix file and return them.

        If the has_prefix file does not exist, None is returned.
        """
        if self.prefix_file is not None:
            for line in self.prefix_file.decode("utf-8").splitlines():
                line = line.strip()
                try:
                    placeholder, mode, filename = line.split()
                    placeholder = placeholder.strip("'\"")
                    filename = filename.strip("'\"")
                except ValueError:
                    placeholder, mode, filename = "/<dummy>/<placeholder>", "text", line

                return (placeholder, mode, filename)
        return None

    def check_prefix_file_filename(self):
        """Check that the filenames in has_prefix exist in the archive."""
        if self.prefix_file_contents is not None:
            _, _, filename = self.prefix_file_contents

            if os.path.normpath(filename) not in self.paths:
                return Error(
                    self.path,
                    "C1129",
                    u'Found filename "{}" in info/has_prefix not included in archive'.format(
                        filename
                    ),
                )

    def check_prefix_file_mode(self):
        """Check that the has_prefix mode is either binary or text."""
        if self.prefix_file_contents is not None:
            _, mode, _ = self.prefix_file_contents

            if mode not in ["binary", "text"]:
                return Error(
                    self.path,
                    "C1130",
                    u'Found invalid mode "{}" in info/has_prefix'.format(mode),
                )

    def check_prefix_file_binary_mode(self):
        """Check that the has_prefix file binary mode is correct."""
        if self.prefix_file_contents is not None:
            placeholder, mode, _ = self.prefix_file_contents

            if mode == "binary":
                if self.name == "python":
                    return Error(
                        self.path,
                        "C1131",
                        "Binary placeholder found in info/has_prefix not allowed when building Python",
                    )
                elif self.win_pkg:
                    return Error(
                        self.path,
                        "C1132",
                        "Binary placeholder found in info/has_prefix not allowed in Windows package",
                    )
                elif len(placeholder) != 255:
                    return Error(
                        self.path,
                        "C1133",
                        u'Binary placeholder "{}" found in info/has_prefix does not have a length of 255 bytes'.format(
                            placeholder
                        ),
                    )

    def check_for_post_links(self):
        """Check the tar archive for pre and post link files."""
        for filepath in self.paths:
            if filepath.endswith(
                (
                    "-post-link.sh",
                    "-pre-link.sh",
                    "-pre-unlink.sh",
                    "-post-link.bat",
                    "-pre-link.bat",
                    "-pre-unlink.bat",
                )
            ):
                return Error(
                    self.path,
                    "C1134",
                    u'Found pre/post link file "{}" in archive'.format(filepath),
                )

    def check_for_egg(self):
        """Check the tar archive for egg files."""
        for filepath in self.paths:
            if filepath.endswith(".egg"):
                return Error(
                    self.path,
                    "C1135",
                    u'Found egg file "{}" in archive'.format(filepath),
                )

    def check_for_easy_install_script(self):
        """Check the tar archive for easy_install scripts."""
        for filepath in self.paths:
            if filepath.startswith(
                (
                    os.path.join("bin", "easy_install"),
                    os.path.join("Scripts", "easy_install"),
                )
            ):
                return Error(
                    self.path,
                    "C1136",
                    u'Found easy_install script "{}" in archive'.format(filepath),
                )

    def check_for_pth_file(self):
        """Check the tar archive for .pth files."""
        for filepath in self.paths:
            if filepath.endswith(".pth"):
                return Error(
                    self.path,
                    "C1137",
                    u'Found namespace file "{}" in archive'.format(
                        os.path.normpath(filepath)
                    ),
                )

    def check_for_pyo_file(self):
        """Check the tar archive for .pyo files"""
        for filepath in self.paths:
            if filepath.endswith(".pyo") and self.name != "python":
                return Error(
                    self.path,
                    "C1138",
                    u'Found pyo file "{}" in archive'.format(filepath),
                )

    def check_for_pyc_in_site_packages(self):
        """Check that .pyc files are only found within the site-packages or disutils directories."""
        for filepath in self.paths:
            if (
                filepath.endswith(".pyc")
                and "site-packages" not in filepath
                and "distutils" not in filepath
            ):
                return Error(
                    self.path,
                    "C1139",
                    u'Found pyc file "{}" in invalid directory'.format(filepath),
                )

    def check_for_2to3_pickle(self):
        """Check the tar archive for .pickle files."""
        for filepath in self.paths:
            if "lib2to3" in filepath and filepath.endswith(".pickle"):
                return Error(
                    self.path,
                    "C1140",
                    u'Found lib2to3 .pickle file "{}"'.format(filepath),
                )

    def check_pyc_files(self):
        """Check that a .pyc file exists for every .py file in a Python 2 package."""
        if "py3" not in self.build:
            for filepath in self.paths:
                if "site-packages" in filepath:
                    if filepath.endswith(".py") and (filepath + "c") not in self.paths:
                        return Error(
                            self.path,
                            "C1141",
                            u'Found python file "{}" without a corresponding pyc file'.format(
                                filepath
                            ),
                        )

    def check_menu_json_name(self):
        """Check that the Menu/package.json filename is identical to the package name."""
        menu_json_files = [
            filepath
            for filepath in self.paths
            if filepath.startswith("Menu" + os.path.sep) and filepath.endswith(".json")
        ]

        if len(menu_json_files) == 1:
            filename = menu_json_files[0]
            if filename != os.path.normpath("{}.json".format(self.name)):
                return Error(
                    self.path,
                    "C1142",
                    u'Found invalid Menu json file "{}"'.format(filename),
                )
        elif len(menu_json_files) > 1:
            return Error(self.path, "C1143", "Found more than one Menu json file")

    def check_windows_arch(self):
        """Check that Windows package .exes and .dlls contain the correct headers."""
        if self.win_pkg:
            arch = self.info["arch"]
            if arch not in ("x86", "x86_64"):
                return Error(
                    self.path,
                    "C1144",
                    u'Found unrecognized Windows architecture "{}"'.format(arch),
                )

            for member in self.archive_members:
                if member.endswith((".exe", ".dll")):
                    with open(os.path.join(self.tmpdir, member), "rb") as file_object:
                        file_header = file_object.read(4096)
                        file_object_type = get_object_type(file_header)
                        if (arch == "x86" and file_object_type != "DLL I386") or (
                            arch == "x86_64" and file_object_type != "DLL AMD64"
                        ):

                            return Error(
                                self.path,
                                "C1145",
                                u'Found file "{}" with object type "{}" but with arch "{}"'.format(
                                    member, file_object_type, arch
                                ),
                            )

    def check_package_hashes_and_size(self):
        """Check the sha256 checksum and filesize of each file in the package."""
        for member in self.archive_members:
            file_path = os.path.join(self.tmpdir, member)
            if member in self.paths_json_path:
                if os.path.isfile(file_path):
                    path = self.paths_json_path[member]
                    size = os.stat(file_path).st_size
                    if size != path["size_in_bytes"]:
                        return Error(
                            self.path,
                            "C1147",
                            'Found file "{}" with filesize different than listed in paths.json'.format(
                                member
                            ),
                        )
                    with open(file_path, "rb") as file_object:
                        sha256_digest = sha256_checksum(file_object)
                    if sha256_digest != path["sha256"]:
                        return Error(
                            self.path,
                            "C1146",
                            'Found file "{}" with sha256 hash different than listed in paths.json'.format(
                                member
                            ),
                        )

    def check_noarch_files(self):
        """Check that noarch packages do not contain architecture specific files."""
        if self.info["subdir"] == "noarch":
            for filepath in self.paths:
                if filepath.endswith((".so", ".dylib", ".dll", "lib")):
                    return Error(
                        self.path,
                        "C1148",
                        u'Found architecture specific file "{}" in package.'.format(
                            filepath
                        ),
                    )


class CondaRecipeCheck(object):
    """Create checks in order to validate conda recipes."""

    def __init__(self, meta, recipe_dir):
        """Initialize conda recipe information for use with recipe checks."""
        super(CondaRecipeCheck, self).__init__()
        self.meta = meta
        self.recipe_dir = recipe_dir
        self.name_pat = re.compile(r"[a-z0-9_][a-z0-9_\-\.]*$")
        self.version_pat = re.compile(r"[\w\.]+$")
        self.url_pat = re.compile(r"(ftp|http(s)?)://")
        self.hash_pat = {
            "md5": re.compile(r"[a-f0-9]{32}$"),
            "sha1": re.compile(r"[a-f0-9]{40}$"),
            "sha256": re.compile(r"[a-f0-9]{64}$"),
        }

    def check_package_name(self):
        """Check the package name in meta.yaml for proper formatting."""
        package_name = self.meta.get("package", {}).get("name", "")

        if package_name == "":
            return Error(self.recipe_dir, "C2101", "Missing package name in meta.yaml")

        if not self.name_pat.match(package_name) or package_name.endswith(
            (".", "-", "_")
        ):
            return Error(
                self.recipe_dir,
                "C2102",
                u'Found invalid package name "{}" in meta.yaml'.format(package_name),
            )

        seq = get_bad_seq(package_name)
        if seq:
            return Error(
                self.recipe_dir,
                "C2103",
                u'Found invalid sequence "{}" in package name'.format(seq),
            )

    def check_package_version(self):
        """Check the package version in meta.yaml for proper formatting."""
        package_version = self.meta.get("package", {}).get("version", "")

        if package_version == "":
            return Error(
                self.recipe_dir, "C2104", "Missing package version in meta.yaml"
            )

        if isinstance(package_version, str):
            if (
                not self.version_pat.match(package_version)
                or package_version.startswith(("_", "."))
                or package_version.endswith(("_", "."))
            ):
                return Error(
                    self.recipe_dir,
                    "C2105",
                    u'Found invalid package version "{}" in meta.yaml'.format(
                        package_version
                    ),
                )

            seq = get_bad_seq(package_version)
            if seq:
                return Error(
                    self.recipe_dir,
                    "C2106",
                    u'Found invalid sequence "{}" in package version'.format(seq),
                )

    def check_build_number(self):
        """Check the build number in meta.yaml for proper formatting."""
        build_number = self.meta.get("build", {}).get("number")

        if build_number is not None:
            try:
                build_number = int(build_number)
                if build_number < 0:
                    return Error(
                        self.recipe_dir,
                        "C2108",
                        "Build number in info/index.json cannot be a negative integer",
                    )

            except ValueError:
                return Error(
                    self.recipe_dir,
                    "C2107",
                    "Build number in info/index.json must be an integer",
                )

    def check_fields(self):
        """Check that the fields listed in meta.yaml are valid."""

        for section in self.meta:
            if section not in FIELDS and section != "extra":
                return Error(
                    self.recipe_dir,
                    "C2109",
                    u'Found invalid section "{}"'.format(section),
                )

            if section != "extra":
                subfield = self.meta.get(section)
                if hasattr(subfield, "keys"):
                    for key in subfield:
                        if key not in FIELDS[section]:
                            return Error(
                                self.recipe_dir,
                                "C2110",
                                u'Found invalid field "{}" in section "{}"'.format(
                                    key, section
                                ),
                            )
                else:
                    # list of dicts.  Used in source and outputs.
                    for entry in subfield:
                        for key in entry:
                            if key not in FIELDS[section]:
                                return Error(
                                    self.recipe_dir,
                                    "C2110",
                                    u'Found invalid field "{}" in section "{}"'.format(
                                        key, section
                                    ),
                                )

    def check_requirements(self):
        """Check that the requirements listed in meta.yaml are valid."""
        build_requirements = self.meta.get("requirements", {}).get("build", [])
        run_requirements = self.meta.get("requirements", {}).get("run", [])

        for requirement in build_requirements + run_requirements:
            requirement_parts = requirement.split()
            requirement_name = requirement_parts[0]

            if not self.name_pat.match(requirement_name):
                if requirement in build_requirements:
                    return Error(
                        self.recipe_dir,
                        "C2111",
                        u'Found invalid build requirement "{}"'.format(requirement),
                    )
                elif requirement in run_requirements:
                    return Error(
                        self.recipe_dir,
                        "C2112",
                        u'Found invalid run requirement "{}"'.format(requirement),
                    )

            if len(requirement_parts) == 0:
                return Error(
                    self.recipe_dir, "C2113", "Found empty dependencies in meta.yaml"
                )

            elif len(requirement_parts) >= 2 and not fullmatch(
                ver_spec_pat, requirement_parts[1]
            ):
                return Error(
                    self.recipe_dir,
                    "C2114",
                    u'Found invalid dependency "{}" in meta.yaml'.format(requirement),
                )

        if len(build_requirements) != len(set(build_requirements)):
            return Error(
                self.recipe_dir,
                "C2115",
                u"Found duplicate build requirements: {}".format(build_requirements),
            )

        if len(run_requirements) != len(set(run_requirements)):
            return Error(
                self.recipe_dir,
                "C2116",
                u"Found duplicate run requirements: {}".format(run_requirements),
            )

    def check_about(self):
        """Check the about field in meta.yaml for proper formatting."""
        summary = self.meta.get("about", {}).get("summary")

        if summary is not None and len(summary) > 80:
            return Error(
                self.recipe_dir,
                "C2117",
                "Found summary with length greater than 80 characters",
            )

        home = self.meta.get("about", {}).get("home")
        dev_url = self.meta.get("about", {}).get("dev_url")
        doc_url = self.meta.get("about", {}).get("doc_url")
        license_url = self.meta.get("about", {}).get("license_url")

        for url in [home, dev_url, doc_url, license_url]:
            if url is not None and not self.url_pat.match(url):
                return Error(
                    self.recipe_dir,
                    "C2118",
                    u'Found invalid URL "{}" in meta.yaml'.format(url),
                )

    def check_source(self):
        """Check the source field in meta.yaml for proper formatting."""
        sources = ensure_list(self.meta.get("source", {}))
        for source in sources:
            url = source.get("url")
            if url is not None:
                if self.url_pat.match(url):

                    for hash_algorithm in ["md5", "sha1", "sha256"]:
                        hexdigest = source.get(hash_algorithm)
                        if hexdigest is not None and not self.hash_pat[
                            hash_algorithm
                        ].match(hexdigest):
                            return Error(
                                self.recipe_dir,
                                "C2119",
                                u'Found invalid hash "{}" in meta.yaml'.format(
                                    hexdigest
                                ),
                            )

                else:
                    return Error(
                        self.recipe_dir,
                        "C2120",
                        u'Found invalid URL "{}" in meta.yaml'.format(url),
                    )

            git_url = source.get("git_url")
            if git_url and (source.get("git_tag") and source.get("git_branch")):
                return Error(
                    self.recipe_dir,
                    "C2121",
                    "Found both git_branch and git_tag in meta.yaml source field",
                )

    def check_license_family(self):
        """Check that the license family listed in meta.yaml is valid."""
        license_family = self.meta.get("about", {}).get(
            "license_family", self.meta.get("about", {}).get("license")
        )

        if license_family is not None and license_family not in LICENSE_FAMILIES:
            return Error(
                self.recipe_dir,
                "C2122",
                u'Found invalid license family "{}"'.format(license_family),
            )

    def check_for_valid_files(self):
        """Check that the files listed in meta.yaml exist."""
        test_files = self.meta.get("test", {}).get("files", [])
        test_source_files = self.meta.get("test", {}).get("source_files", [])
        sources = ensure_list(self.meta.get("source", {}))
        source_patches = []
        for source in sources:
            source_patches.extend(source.get("patches", []))

        for filename in test_files + test_source_files + source_patches:
            filepath = os.path.join(self.recipe_dir, filename)
            if filename.startswith(".."):
                return Error(
                    self.recipe_dir,
                    "C2123",
                    u'Found file "{}" listed outside recipe directory'.format(filename),
                )

            if not os.path.exists(filepath):
                return Error(
                    self.recipe_dir,
                    "C2124",
                    u'Found file "{}" in meta.yaml that doesn\'t exist'.format(
                        filename
                    ),
                )

    def check_dir_content(self):
        """Check for disallowed files inside the recipe directory."""
        disallowed_extensions = (
            ".tar",
            ".tar.gz",
            ".tar.bz2",
            ".tar.xz",
            ".so",
            ".dylib",
            ".la",
            ".a",
            ".dll",
            ".pyd",
        )

        for dirpath, _, filenames in os.walk(self.recipe_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if filepath.endswith(disallowed_extensions):
                    return Error(
                        self.recipe_dir,
                        "C2125",
                        u'Found disallowed file with extension "{}"'.format(filepath),
                    )

    def check_recipes_comments(self):
        """Check for default comments in conda-forge example recipe."""
        meta = os.path.join(self.recipe_dir, "meta.yaml")
        with open(meta) as meta_file:
            recipe = meta_file.read().splitlines()

        for line in recipe:
            if line.startswith("#") and line in CONDA_FORGE_COMMENTS.splitlines():
                return Error(
                    self.recipe_dir,
                    "C2126",
                    "Found conda-forge comment in meta.yaml file",
                )
