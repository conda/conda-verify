# -*- coding: utf-8 -*-
import sys

from conda_verify.checks import CondaPackageCheck, CondaRecipeCheck
from conda_verify.errors import PackageError


class Verify(object):

    @staticmethod
    def verify_package(path_to_package=None):
        package_check = CondaPackageCheck(path_to_package)

        checks_to_display = [getattr(package_check, method)() for method
                             in dir(package_check) if method.startswith('check') and
                             getattr(package_check, method)() is not None]

        return_code = 0

        for check in sorted(checks_to_display):
            print(check, file=sys.stderr)
            return_code = 1

        if return_code > 0:
            sys.exit(return_code)

    @staticmethod
    def verify_recipe(rendered_meta=None, recipe_dir=None):
        recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
        recipe_check.check_fields()
        recipe_check.check_source()
        recipe_check.check_requirements()
        recipe_check.validate_files()
        recipe_check.check_about()
        recipe_check.check_license_family()
        recipe_check.check_dir_content()
