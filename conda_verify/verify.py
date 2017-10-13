# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

from conda_verify.checks import CondaPackageCheck, CondaRecipeCheck
from conda_verify.errors import PackageError, RecipeError
from conda_verify.utilities import ensure_list


class Verify(object):
    """Verify class is called by the CLI but may be used as an API as well."""

    @staticmethod
    def verify_package(path_to_package=None, checks_to_ignore=None, exit_on_error=False):
        """Run all package checks in order to verify a conda package."""
        package_check = CondaPackageCheck(path_to_package)

        # collect all CondaPackageCheck methods that start with the word 'check'
        # this should later be a decorator that is placed on each check
        checks_to_display = [getattr(package_check, method)() for method
                             in dir(package_check) if method.startswith('check') and
                             getattr(package_check, method)() is not None]

        return_code = 0

        if len(checks_to_display) > 0:
            for check in sorted(checks_to_display):
                if check.code not in ensure_list(checks_to_ignore):
                    check = u'{}' .format(check)
                    if exit_on_error:
                        raise PackageError(check)
                    else:
                        print(check, file=sys.stderr)

                    return_code = 1

        # by exiting at a return code greater than 0 we can assure failures
        # in logs or continuous integration services
        if return_code > 0:
            sys.exit(return_code)

    @staticmethod
    def verify_recipe(rendered_meta=None, recipe_dir=None, checks_to_ignore=None,
                      exit_on_error=False):
        """Run all recipe checks in order to verify a conda recipe."""
        recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)

        # collect all CondaRecipeCheck methods that start with the word 'check'
        # this should later be a decorator that is placed on each check
        checks_to_display = [getattr(recipe_check, method)() for method
                             in dir(recipe_check) if method.startswith('check') and
                             getattr(recipe_check, method)() is not None]

        return_code = 0

        if len(checks_to_display) > 0:
            for check in sorted(checks_to_display):
                if check.code not in ensure_list(checks_to_ignore):
                    if exit_on_error:
                        raise RecipeError(check)
                    else:
                        print(check, file=sys.stderr)

                    return_code = 1

        # by exiting at a return code greater than 0 we can assure failures
        # in logs or continuous integration services
        if return_code > 0:
            sys.exit(return_code)
