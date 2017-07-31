import os
import sys

from optparse import OptionParser

from conda_verify.errors import RecipeError
from conda_verify.verify import Verify
from conda_verify.utilities import render_metadata, iter_cfgs


def cli():
    p = OptionParser(
        usage="usage: %prog [options] <path to recipes or packages>",
        description="tool for (passively) verifying conda recipes and conda "
                    "packages for the Anaconda distribution")

    p.add_option('-v', '--version',
                 help="display the version being used and exit",
                 action="store_true")

    opts, args = p.parse_args()

    if opts.version:
        from conda_verify import __version__
        sys.exit('conda-verify {}' .format(__version__))

    verifier = Verify()
    for path in args:
        meta_file = os.path.join(path, 'meta.yaml')
        if os.path.isfile(meta_file):
            print('Verifying {}...' .format(meta_file))
            for cfg in iter_cfgs():
                meta = render_metadata(path, cfg)
                try:
                    verifier.verify_recipe(rendered_meta=meta, recipe_dir=path)
                except RecipeError as e:
                    sys.stderr.write("RecipeError: %s\n" % e)

        elif path.endswith(('.tar.bz2', '.tar')):
            print('Verifying {}...' .format(path))
            verifier.verify_package(path_to_package=path)
