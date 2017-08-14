# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from logging import getLogger
from os.path import dirname, join, lexists
import pkgutil
import tarfile
from tempfile import mkdtemp

from conda.exports import rm_rf

log = getLogger(__name__)


class Verify(object):
    def __init__(self):
        pass

    def list_script(self, path_to_script, run_scripts=None, ignore_scripts=None):
        verify_modules = pkgutil.iter_modules([path_to_script])
        files = []
        for _, name, _ in verify_modules:
            files.append(name)

        if ignore_scripts is not None:
            return [script for script in files if script not in ignore_scripts]
        elif run_scripts is not None:
            return [script for script in files if script in run_scripts]
        else:
            return files

    def verify_recipe(self, run_scripts=None, ignore_scripts=None, **kwargs):
        rec_path = join(dirname(__file__), "recipe")
        files = self.list_script(rec_path, run_scripts=run_scripts, ignore_scripts=ignore_scripts)
        for script in files:
            mod = getattr(__import__("conda_verify.recipe", fromlist=[script]), script)
            print("Running script: %s" % script)
            mod.verify(**kwargs)

    def verify_package(self, run_scripts=None, ignore_scripts=None, **kwargs):
        path_to_package = kwargs['path_to_package']
        extracted_package_dir = mkdtemp()

        try:
            extract_tarball(path_to_package, extracted_package_dir)
            kwargs['extracted_package_dir'] = extracted_package_dir

            pkg_path = join(dirname(__file__), "package")
            files = self.list_script(pkg_path, run_scripts=run_scripts, ignore_scripts=ignore_scripts)
            for script in files:
                mod = getattr(__import__("conda_verify.package", fromlist=[script]), script)
                print("Running script: %s" % script)
                mod.verify(**kwargs)

        finally:
            rm_rf(extracted_package_dir)


def extract_tarball(tarball_full_path, destination_directory=None, progress_update_callback=None):
    if destination_directory is None:
        destination_directory = tarball_full_path[:-8]
    log.debug("extracting %s\n  to %s", tarball_full_path, destination_directory)

    assert not lexists(destination_directory), destination_directory

    with tarfile.open(tarball_full_path) as t:
        members = t.getmembers()
        num_members = len(members)

        def members_with_progress():
            for q, member in enumerate(members):
                if progress_update_callback:
                    progress_update_callback(q / num_members)
                yield member

        t.extractall(path=destination_directory, members=members_with_progress())
