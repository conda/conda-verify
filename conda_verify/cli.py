import os
import sys

import click

from conda_verify import __version__
from conda_verify.verify import Verify
from conda_verify.utilities import render_metadata, iter_cfgs


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--version')
def cli(path, version):
    """"""
    if version:
        sys.exit('conda-verify {}' .format(__version__))

    verifier = Verify()
    meta_file = os.path.join(path, 'meta.yaml')
    if os.path.isfile(meta_file):
        print('Verifying {}...' .format(meta_file))
        for cfg in iter_cfgs():
            meta = render_metadata(path, cfg)
            verifier.verify_recipe(rendered_meta=meta, recipe_dir=path)

    elif path.endswith(('.tar.bz2', '.tar')):
        print('Verifying {}...' .format(path))
        verifier.verify_package(path_to_package=path)
