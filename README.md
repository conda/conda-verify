anaconda-verify
===============

anaconda-verify is a tool for (passively) verifying conda recipes and
conda packages.

All <a href="https://github.com/ContinuumIO/anaconda-recipes">
Anaconda recipes</a>, as well as
the <a href="http://repo.continuum.io/pkgs/free/">Anaconda packages</a>
need to pass this tool before they are made publically available.

Using anaconda-verify:

    $ conda install anaconda-verify
    $ anaconda-verify -h
    $ anaconda-verify <path to recipes or packages>


The purpose of this verification process is to ensure that recipes don't
contain obvious bugs, and that the conda packages we distribute to millions
of users meet our high quality standards.

Historically, the conda packages which represent the Anaconda distribution
were not created using `conda-build`, but an internal build system.
In fact, `conda-build` started as a public fork of this internal system
3 years ago.  At that point the Anaconda distribution had already been
around for almost a year, and the only way to create conda packages
was by using the internal system.
While `conda-build` has made a lot of progress, the internal system basically
stayed unchanged, because the needs on a system for building a distribution
are quite different, and not driven by the community using `conda-build`
for continuous integration and other language support (e.g. Perl, Lua), etc. .
On the other hand, the internal system has been developed to support
Anaconda distribution specific needs, such as MKL featured packages,
source and license reference meta-data, and interoperability between
collections of packages.

In an effort to bridge the gap between our internal system and `conda-build`,
we started using `conda-build` to create conda packages for the Anaconda
distribution itself about one year ago.
By now, more than 85% of the conda packages in the Anaconda distribution
are created using `conda-build`.
However, because the different requirements mentioned above, we only allow
certain features that `conda-build` offers.
This also helps to keep
the <a href="https://github.com/ContinuumIO/anaconda-recipes">Anaconda
recipes</a> simple and maintainable, and functional with the rest of the
internal system which reads meta-data from the recipes.
This is why we require conda recipes to be valid according to this tool.


Packages
--------

Another aspect of `anaconda-verify` is the ability to verify conda packages.
These are the most important checks `anaconda-verify` performs on conda
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

    $ anaconda-verify bitarray-0.8.1-py35_0.tar.bz2
    ==> /Users/ilan/aroot/tars64/bitarray-0.8.1-py35_0.tar.bz2 <==
        bitarray

In this case all is fine, and we see that only the `bitarray` directory is
created in `site-packages`.
