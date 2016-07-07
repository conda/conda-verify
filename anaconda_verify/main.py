from __future__ import print_function, division, absolute_import

import sys
from os.path import isfile, join
from optparse import OptionParser

from anaconda_verify.recipe import validate_recipe, RecipeError
from anaconda_verify.package import validate_package, PackageError


def main():
    p = OptionParser(
        usage="usage: %prog [options] <path to recipes or packages>",
        description="tool for (passively) verifying conda recipes and conda "
                    "packages for the Anaconda distribution")

    p.add_option('-e', "--exit",
                 help="on error exit",
                 action="store_true")

    p.add_option('-q', "--quiet",
                 action="store_true")

    p.add_option('-V', '--version',
                 help="display the version being used and exit",
                 action="store_true")

    opts, args = p.parse_args()
    verbose = not opts.quiet
    if opts.version:
        from anaconda_verify import __version__
        print('anaconda-verify version:', __version__)
        return

    for path in args:
        if isfile(join(path, 'meta.yaml')):
            if verbose:
                print("==> %s <==" % path)
            try:
                validate_recipe(path)
            except RecipeError as e:
                sys.stderr.write("RecipeError: %s\n" % e)
                if opts.exit:
                    sys.exit(1)

        elif path.endswith('.tar.bz2'):
            if verbose:
                print("==> %s <==" % path)
            try:
                validate_package(path, verbose)
            except PackageError as e:
                sys.stderr.write("PackageError: %s\n" % e)
                if opts.exit:
                    sys.exit(1)

        else:
            if verbose:
                print("Ignoring: %s" % path)


if __name__ == '__main__':
    main()
