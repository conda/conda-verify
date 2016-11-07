conda-verify
============

conda-verify is a tool for (passively) verifying conda recipes and
conda packages.

Using conda-verify:

    $ conda install conda-verify
    $ conda-verify -h
    $ conda-verify <path to recipes or packages>


The purpose of this verification process is to ensure that recipes don't
contain obvious bugs, and that the conda packages we distribute to millions
of users meet our high quality standards.


Packages
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

Here is an example of running the tool on conda packages:

    $ conda-verify bitarray-0.8.1-py35_0.tar.bz2
    ==> /Users/ilan/aroot/tars64/bitarray-0.8.1-py35_0.tar.bz2 <==
        bitarray

In this case all is fine, and we see that only the `bitarray` directory is
created in `site-packages`.
