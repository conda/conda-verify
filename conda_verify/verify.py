import pkgutil
from os.path import join, dirname


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
        pkg_path = join(dirname(__file__), "package")
        files = self.list_script(pkg_path, run_scripts=run_scripts, ignore_scripts=ignore_scripts)
        for script in files:
            mod = getattr(__import__("conda_verify.package", fromlist=[script]), script)
            print("Running script: %s" % script)
            mod.verify(**kwargs)
