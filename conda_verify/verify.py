# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

from conda_verify.checks import CondaPackageCheck, CondaRecipeCheck
from conda_verify.utilities import ensure_list


class Verify(object):

    @staticmethod
    def verify_package(path_to_package=None, checks_to_ignore=None, exit_on_error=False):
        package_check = CondaPackageCheck(path_to_package)

        checks_to_display = [getattr(package_check, method)() for method
                             in dir(package_check) if method.startswith('check') and
                             getattr(package_check, method)() is not None]

        return_code = 0

        for check in sorted(checks_to_display):
            if check.code not in ensure_list(checks_to_ignore):
                print(check, file=sys.stderr)
                return_code = 1

        if return_code > 0:
            sys.exit(return_code)

    @staticmethod
    def verify_recipe(rendered_meta=None, recipe_dir=None, checks_to_ignore=None,
                      exit_on_error=False):
        recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)

        checks_to_display = [getattr(recipe_check, method)() for method
                             in dir(recipe_check) if method.startswith('check') and
                             getattr(recipe_check, method)() is not None]

        return_code = 0

        for check in sorted(checks_to_display):
            print(check, file=sys.stderr)
            return_code = 1

        if return_code > 0:
            sys.exit(return_code)
