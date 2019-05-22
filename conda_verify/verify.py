# -*- coding: utf-8 -*-
from __future__ import print_function

from conda_verify.checks import CondaPackageCheck, CondaRecipeCheck
from conda_verify.errors import PackageError, RecipeError
from conda_verify.utilities import ensure_list
from logging import getLogger


class Verify(object):
    """Verify class is called by the CLI but may be used as an API as well."""

    @staticmethod
    def verify_package(
        path_to_package=None, checks_to_ignore=None, exit_on_error=False, **kw
    ):
        """Run all package checks in order to verify a conda package.
        checks_to_ignore should be a list, tuple, or set of codes, such as ['C1102', 'C1104'].
        Codes are listed in readme.md.  Package codes follow 1xxx, recipe codes follow 2xxx."""
        package_check = CondaPackageCheck(path_to_package)

        if ("ignore_scripts" in kw and kw["ignore_scripts"]) or (
            "run_scripts" in kw and kw["run_scripts"]
        ):
            getLogger(__name__).warn(
                "Ignoring legacy ignore_scripts or run_scripts.  These have "
                "been replaced by the checks_to_ignore argument, which takes a"
                "list of codes, documented at https://github.com/conda/conda-verify#checks"
            )

        # collect all CondaPackageCheck methods that start with the word 'check'
        # this should later be a decorator that is placed on each check
        checks_to_display = []
        for method in dir(package_check):
            if method.startswith("check"):
                # runs the check
                #  TODO: should have a way to skip checks if a check's codes are all ignored
                check = getattr(package_check, method)()
                if check is not None and check.code not in ensure_list(
                    checks_to_ignore
                ):
                    checks_to_display.append(check)

        if checks_to_display and exit_on_error:
            raise PackageError(check)
        return (
            path_to_package,
            sorted(["[{}] {}".format(*c[1:]) for c in checks_to_display]),
        )

    @staticmethod
    def verify_recipe(
        rendered_meta=None,
        recipe_dir=None,
        checks_to_ignore=None,
        exit_on_error=False,
        **kw
    ):
        """Run all recipe checks in order to verify a conda recipe.
        checks_to_ignore should be a list, tuple, or set of codes, such as ['C2102', 'C2104'].
        Codes are listed in readme.md.  Package codes follow 1xxx, recipe codes follow 2xxx."""
        recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)

        if ("ignore_scripts" in kw and kw["ignore_scripts"]) or (
            "run_scripts" in kw and kw["run_scripts"]
        ):
            getLogger(__name__).warn(
                "Ignoring legacy ignore_scripts or run_scripts.  These have "
                "been replaced by the checks_to_ignore argument, which takes a"
                "list of codes, documented at https://github.com/conda/conda-verify#checks"
            )

        checks_to_display = []
        for method in (_ for _ in dir(recipe_check) if _.startswith("check_")):
            check = getattr(recipe_check, method)()
            if check and check.code not in ensure_list(checks_to_ignore):
                checks_to_display.append(check)

        if checks_to_display and exit_on_error:
            raise RecipeError(checks_to_display[0])
        return (
            recipe_dir,
            sorted(["[{}] {}".format(*c[1:]) for c in checks_to_display]),
        )
