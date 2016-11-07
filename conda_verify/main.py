from __future__ import print_function, division, absolute_import

import sys
from os.path import isfile, join
from optparse import OptionParser

from conda_verify.exceptions import RecipeError, PackageError
from conda_verify.verify import Verify
from conda_verify.utils import render_metadata, iter_cfgs


def main():
    p = OptionParser(
        usage="usage: %prog [options] <path to recipes or packages>",
        description="tool for (passively) verifying conda recipes and conda "
                    "packages for the Anaconda distribution")

    p.add_option('-e', "--exit",
                 help="on error exit",
                 action="store_true")

    p.add_option('-p', "--pedantic",
                 action="store_true")

    p.add_option('-q', "--quiet",
                 action="store_true")

    p.add_option('-V', '--version',
                 help="display the version being used and exit",
                 action="store_true")

    opts, args = p.parse_args()
    verbose = not opts.quiet
    if opts.version:
        from conda_verify import __version__
        print('conda-verify version:', __version__)
        return

    verifier = Verify()
    for path in args:
        if isfile(join(path, 'meta.yaml')):
            if verbose:
                print("==> %s <==" % path)
            for cfg in iter_cfgs():
                meta = render_metadata(path, cfg)
                try:
                    verifier.verify_recipe(pedantic=opts.pedantic, rendered_meta=meta,
                                           recipe_dir=path)
                except RecipeError as e:
                    sys.stderr.write("RecipeError: %s\n" % e)
                    if opts.exit:
                        sys.exit(1)

        elif path.endswith('.tar.bz2'):
            if verbose:
                print("==> %s <==" % path)
            try:
                verifier.verify_package(pedantic=opts.pedantic, path_to_package=path,
                                        verbose=verbose)
            except PackageError as e:
                sys.stderr.write("PackageError: %s\n" % e)
                if opts.exit:
                    sys.exit(1)

        else:
            if verbose:
                print("Ignoring: %s" % path)


if __name__ == '__main__':
    main()
