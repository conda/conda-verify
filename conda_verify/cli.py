from __future__ import print_function
import json
import os
import sys
from glob import glob

import click
import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

from conda_verify import __version__
from conda_verify.verify import Verify
from conda_verify.utilities import DummyExecutor, render_metadata, iter_cfgs


def _submit_verify_recipe(path, executor, ignore):
    futures = []
    for cfg in iter_cfgs():
        meta = render_metadata(path, cfg)
        if meta.get("build", {}).get("skip", "").lower() != "true":
            futures.append(
                executor.submit(
                    Verify.verify_recipe,
                    rendered_meta=meta,
                    recipe_dir=path,
                    checks_to_ignore=ignore,
                    exit_on_error=False,
                )
            )
    return futures


def _submit_verify_package(path, ignore):
    package_issues = (path, None)
    try:
        package_issues = Verify.verify_package(
            path_to_package=path, checks_to_ignore=ignore, exit_on_error=False
        )
    except (KeyError, OSError) as e:
        package_issues = (path, [str(e)])
    return package_issues


@click.command()
@click.argument("paths", nargs=-1, type=str)
@click.option("--ignore", nargs=1, type=str)
@click.option("--exit", is_flag=True)
@click.option("--debug", is_flag=True)
@click.option("--out-file", nargs=1, type=click.Path())
@click.version_option(prog_name="conda-verify", version=__version__)
def cli(paths, ignore, exit, debug, out_file):
    """conda-verify is a tool for validating conda packages and recipes.

    To validate a package:\n
    $  conda-verify path/to/package.tar.bz2

    To validate a recipe:\n
    $  conda-verify path/to/recipe_directory/
    """
    if ignore:
        ignore = ignore.split(",")

    package_issues = {}
    futures = []
    paths_glob = []
    for path in paths:
        glob_paths = glob(os.path.expanduser(path))
        if not glob_paths:
            print("Error: path spec %s didn't match any files" % path)
            sys.exit(1)
        paths_glob.extend(glob_paths)
    with (DummyExecutor if debug else ProcessPoolExecutor)() as executor:
        for path in paths_glob:
            meta_file = os.path.join(path, "meta.yaml")
            if os.path.isfile(meta_file):
                futures.extend(_submit_verify_recipe(path, executor, ignore))
            elif path.endswith((".tar.bz2", ".tar", ".conda")):
                futures.append(executor.submit(_submit_verify_package, path, ignore))
        for f in tqdm.tqdm(as_completed(futures), total=len(futures), leave=False):
            path, issues = f.result()
            if issues:
                package_issues[path] = issues

    if out_file:
        with open(out_file, "w") as f:
            json.dump(package_issues, f)
            print("saved to %s" % out_file)
    else:
        for path, issues in package_issues.items():
            print("-" * len(path))
            print(path)
            print("-" * len(path))
            for check in sorted(issues):
                try:
                    print(check, file=sys.stderr)
                except UnicodeEncodeError:
                    print(
                        "Could not print message for error code {} due to unicode error".format(
                            check.code
                        ),
                        file=sys.stderr,
                    )

    if exit and package_issues:
        sys.exit(1)
