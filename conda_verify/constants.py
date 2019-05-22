try:
    from conda_build.license_family import allowed_license_families as LICENSE_FAMILIES
except ImportError:
    print(
        "warning: could not import conda-build ALLOWED_LICENSE_FAMILIES data.  Falling back to "
        "possibly stale static list"
    )
    LICENSE_FAMILIES = [
        "AGPL",
        "GPL",
        "GPL2",
        "GPL3",
        "LGPL",
        "BSD",
        "MIT",
        "APACHE",
        "PSF",
        "CC",
        "PUBLIC-DOMAIN",
        "PROPRIETARY",
        "OTHER",
        "NONE",
    ]

try:
    from conda_build.metadata import FIELDS
except ImportError:
    print(
        "warning: could not import conda-build FIELDS data.  Falling back to possibly stale"
        "static list"
    )
    FIELDS = {
        "package": {"name", "version"},
        "source": {
            "fn",
            "url",
            "md5",
            "sha1",
            "sha256",
            "git_url",
            "git_tag",
            "git_branch",
            "git_rev",
            "patches",
            "hg_url",
            "hg_tag",
            "path",
        },
        "build": {
            "features",
            "track_features",
            "skip",
            "number",
            "entry_points",
            "osx_is_app",
            "noarch",
            "preserve_egg_dir",
            "win_has_prefix",
            "no_link",
            "ignore_prefix_files",
            "msvc_compiler",
            "skip_compile_pyc",
            "detect_binary_files_with_prefix",
            "script",
            "always_include_files",
            "binary_relocation",
            "binary_has_prefix_files",
            "noarch_python",
            "run_exports",
        },
        "requirements": {
            "build",
            "run",
            "preferred_env",
            "host",
            "preferred_env_executable_paths",
        },
        "outputs": {
            "name",
            "build",
            "about",
            "test",
            "version",
            "script",
            "requirements",
            "run_exports",
        },
        "app": {"entry", "icon", "summary", "type", "cli_opts"},
        "test": {"requires", "commands", "files", "source_files", "imports"},
        "about": {
            "license",
            "license_url",
            "license_family",
            "license_file",
            "summary",
            "description",
            "home",
            "doc_url",
            "doc_source_url",
            "dev_url",
        },
        "extra": {"recipe-maintainers", "final", "parent_recipe"},
    }

MAGIC_HEADERS = {
    b"\xca\xfe\xba\xbe": "MachO-universal",
    b"\xce\xfa\xed\xfe": "MachO-i386",
    b"\xcf\xfa\xed\xfe": "MachO-x86_64",
    b"\xfe\xed\xfa\xce": "MachO-ppc",
    b"\xfe\xed\xfa\xcf": "MachO-ppc64",
    b"MZ\x90\x00": "DLL",
    b"\x7fELF": "ELF",
}

DLL_TYPES = {
    0x0: "UNKNOWN",
    0x1D3: "AM33",
    0x8664: "AMD64",
    0x1C0: "ARM",
    0xEBC: "EBC",
    0x14C: "I386",
    0x200: "IA64",
    0x9041: "M32R",
    0x266: "MIPS16",
    0x366: "MIPSFPU",
    0x466: "MIPSFPU16",
    0x1F0: "POWERPC",
    0x1F1: "POWERPCFP",
    0x166: "R4000",
    0x1A2: "SH3",
    0x1A3: "SH3DSP",
    0x1A6: "SH4",
    0x1A8: "SH5",
    0x1C2: "THUMB",
    0x169: "WCEMIPSV2",
}

CONDA_FORGE_COMMENTS = """
# Note: there are many handy hints in comments in this example -- remove them when you've finalized your recipe
# Jinja variables help maintain the recipe as you'll update the version only here.
# sha256 is the prefered checksum -- you can get it for a file with:
#  `openssl sha256 <file name>`.
# You may need the openssl package, available on conda-forge
#  `conda install openssl -c conda-forge``
# If the installation is complex, or different between Unix and Windows, use separate bld.bat and build.sh files instead of this key.
# By default, the package will be built for the Python versions supported by conda-forge and for all major OSs.
# Add the line "skip: True  # [py<35]" (for example) to limit to Python 3.5 and newer, or "skip: True  # [not win]" to limit to Windows.
# When setuptools is available add the `--single-version-externally-managed --record record.txt` above.
# if your project compiles code (such as a C extension) then add `toolchain` as a build requirement.
# Some package might need a `test/commands` key to check CLI.
# List all the packages/modules that `run_test.py` imports.
# Remember to specify the license variants for BSD, Apache, GPL, and LGLP.
# Prefer the short version, e.g: GPL-2.0 instead of GNU General Public License version 2.0
# See https://opensource.org/licenses/alphabetical
# The license_family, i.e. "BSD" if license is "BSD-3-Clause". (optional)
# It is strongly encouraged to include a license file in the package,
# (even if the license doesn't require it) using the license_file entry.
# See http://conda.pydata.org/docs/building/meta-yaml.html#license-file
# The remaining entries in this section are optional, but recommended
# GitHub IDs for maintainers of the recipe.
# Always check with the people listed below if they are OK becoming maintainers of the recipe. (There will be spam!)
"""
