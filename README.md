conda-verify
============
[![Travis branch](https://img.shields.io/travis/conda/conda-verify/master.svg?style=flat-square)](https://travis-ci.org/conda/conda-verify)
[![Codecov branch](https://img.shields.io/codecov/c/github/conda/conda-verify/master.svg?style=flat-square)](https://codecov.io/gh/conda/conda-verify)

conda-verify is a tool for (passively) verifying conda recipes and
conda packages. The purpose of this verification process is to ensure that
recipes don't contain obvious bugs, and that the conda packages we distribute
to millions of users meet our high quality standards.

Features
--------

Another aspect of `conda-verify` is the ability to verify conda packages.
These are the most important checks `conda-verify` performs on conda
packages, and more importantly we explain why these checks are necessary
or useful.

  * Ensure the content of `info/files` corresponds to the actual archived
    files in the tarball (except the ones in `info/`, obviously).  This
    is important, because the files listed in `info/files` determine which
    files are linked into the conda environment.  Any mismatch here would
    indicate either (i) the tarball contains files which are not getting
    linked anywhere or (ii) files which do no exist are attempted to get
    linked (which would result in an error).

  * Check for now allowed archives in the tarball.  A conda package should
    not contain files in the following directories `conda-meta/`,
    `conda-bld/`, `pkgs/`, `pkgs32/` and `envs/`, because this would (for
    example) allow a conda package to modify another existing environment.

  * Make sure the `name`, `version` and `build` values exist in
    `info/index.json` and that they correspond to the actual filename.

  * Ensure there are no files with both `.bat` and `.exe` extension.  For
    example, if you had `Scripts/foo.bat` and `Scripts/foo.exe` one would
    shadow the other, and this would become confusing which one is actually
    executed when the user types `foo`.  Although this check is always done,
    it is only relevant on Windows.

  * Ensure no `easy-install.pth` file exists.  These files would cause
    problems as they would overlap (two or more conda packages would
    contain a `easy-install.pth` file, which overwrite each other when
    installing the package).

  * Ensure no "easy install scripts" exists.  These are entry point scripts
    which setuptools creates which are extremely brittle, and should by
    replaced (overwritten) by the simple entry points scripts `conda-build`
    offers (use `build/entry_points` in your `meta.yaml`).

  * Ensure there are no `.pyd` or `.so` files have a `.py` file next to it.
    This is just confusing, as it is not obvious which one the Python
    interpreter will import.  Under certain circumstances setuptools creates
    `.py` next to shared object files for obscure reasons.

  * For packages (other than `python`), ensure that `.pyc` are not in
    Python's standard library directory.  This would happen when a `.pyc` file
    is missing from the standard library, and then created during the
    build process of another package.

  * Check for missing `.pyc` files.  Missing `.pyc` files cause two types of
    problems: (i) When building new packages, they might get included in
    the new package.  For example, when building scipy and numpy is missing
    `.pyc` files, then these (numpy `.pyc` files) get included in the scipy
    package (ii) There was a (buggy) Python release which would crash when
    `.pyc` files could not written (due to file permissions).

  * Ensure Windows conda packages only contain object files which have the
    correct architecture.  There was a bug in `conda-build` which would
    create `64-bit` entry point executables when building `32-bit` packages
    on a `64-bit` system.

  * Ensure that `site-packages` does not contain certain directories when
    building packages.  For example, when you build `pandas` you don't
    want a `numpy`, `scipy` or `setuptools` directory to be contained in
    the `pandas` package.  This would happen when the `pandas` build
    dependencies have missing `.pyc` files.

Installation
------------

conda-verify can be installed with conda with the following command:
```
$  conda install conda-verify
```

If you would rather install from source, the following commands may be used:
```
$  git clone https://github.com/conda/conda-verify.git
$  cd conda-verify
$  python setup.py install
```


Usage
-----

    usage: conda-verify [options] path

    positional arguments:
        path                    The filepath to the conda package or the path to the recipe directory

    optional arguments:
        --ignore                Ignore specific checks. Each check must be separated by a single comma
        --exit                  Raise an exception after the first error is found


For example, to verify the conda-build recipe while ignoring the field check
and the license check one could run:

    $  conda-verify conda-build/conda.recipe --ignore=C2109,C2124


Checks
------

    C1101 - Missing package name in info/index.json
    C1102 - Found package name in info/index.json "{}" does not match filename "{}"
    C1103 - Found invalid package name in info/index.json
    C1104 - Missing package version in info/index.json
    C1105 - Found invalid version number in info/index.json
    C1106 - Found package version in info/index.json "{}" does not match filename version "{}"
    C1107 - Package version in info/index.json cannot start or end with '_' or '.'
    C1108 - Build number in info/index.json must be an integer
    C1109 - Build number in info/index.json cannot be a negative integer
    C1110 - Found invalid build string "{}" in info/index.json
    C1111 - Found build number in info/index.json "{}" does not match build number "{}" in filename
    C1112 - Missing "depends" field in info/index.json
    C1113 - Found empty dependencies in info/index.json
    C1114 - Found invalid dependency "{}" in info/index.json
    C1115 - Found invalid license "{}" in info/index.json
    C1116 - Found non-ascii characters inside info/index.json
    C1117 - Found duplicate members inside tar archive
    C1118 - Found archive member names containing non-ascii characters
    C1119 - Found filenames in info/files containing non-ascii characters
    C1120 - Found filenames in info/files that start with "info"
    C1121 - Found duplicate filenames in info/files
    C1122 - Found filename in info/files missing from tar archive: {}
    C1123 - Found filename in tar archive missing from info/files: {}
    C1124 - Found hardlink {} in tar archive
    C1125 - Found unallowed file in tar archive: {}
    C1126 - Found {} however package is not a noarch package
    C1127 - Found both .bat and .exe files in executable directory
    C1128 - Found non-ascii characters in info/has_prefix
    C1129 - Found filename "{}" in info/has_prefix not included in archive
    C1130 - Found invalid mode "{}" in info/has_prefix
    C1131 - Binary placeholder found in info/has_prefix not allowed when building Python
    C1132 - Binary placeholder found in info/has_prefix not allowed in Windows package
    C1133 - Binary placeholder "{}" found in info/has_prefix does not have a length of 255 bytes
    C1134 - Found pre/post link file "{}" in archive
    C1135 - Found egg file "{}" in archive
    C1136 - Found easy_install script "{}" in archive
    C1137 - Found namespace file "{}" in archive
    C1138 - Found pyo file "{}" in archive
    C1139 - Found pyc file "{}" in invalid directory
    C1140 - Found lib2to3 .pickle file "{}"
    C1141 - Found python file "{}" without a corresponding pyc file
    C1142 - Found invalid Menu json file "{}"
    C1143 - Found more than one Menu json file
    C1144 - Found unrecognized Windows architecture "{}"
    C1145 - Found file "{}" with object type "{}" but with arch "{}"
    C1146 - Found file "{}" with sha256 hash different than listed in paths.json
    C1147 - Found file "{}" with filesize different than listed in paths.json
    C2101 - Missing package name in meta.yaml
    C2102 - Found invalid package name "{}" in meta.yaml
    C2103 - Found invalid sequence "{}" in package name
    C2104 - Missing package version in meta.yaml
    C2105 - Found invalid package version "{}" in meta.yaml
    C2106 - Found invalid sequence "{}" in package version
    C2107 - Build number in info/index.json must be an integer
    C2108 - Build number in info/index.json cannot be a negative integer
    C2109 - Found invalid section "{}"
    C2110 - Found invalid field "{}" in section "{}"
    C2111 - Found invalid build requirement "{}"
    C2112 - Found invalid run requirement "{}"
    C2113 - Found empty dependencies in info/index.json
    C2114 - Found invalid dependency "{}" in info/index.json
    C2115 - Found duplicate build requirements: {}
    C2116 - Found duplicate run requirements: {}
    C2117 - Found summary with length greater than 80 characters
    C2118 - Found invalid URL "{}" in meta.yaml
    C2119 - Found invalid hash "{}" in meta.yaml
    C2120 - Found invalid URL "{}" in meta.yaml
    C2121 - Found both git_branch and git_tag in meta.yaml source field
    C2122 - Found invalid license family "{}"
    C2123 - Found file "{}" listed outside recipe directory
    C2124 - Found file "{}" in meta.yaml that doesn't exist
    C2125 - Found disallowed file with extension "{}"
    C2126 - Found conda-forge comment in meta.yaml file
