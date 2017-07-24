# -*- coding: utf-8 -*-
from conda_verify.checks import CondaPackageCheck, CondaRecipeCheck


class Verify(object):

    @staticmethod
    def verify_package(path_to_package=None, verbose=True):
        package_check = CondaPackageCheck(path_to_package, verbose)
        package_check.check_duplicate_members()
        package_check.check_index_encoding()
        package_check.check_members()
        package_check.info_files()
        package_check.no_hardlinks()
        package_check.not_allowed_files()
        package_check.index_json()
        package_check.no_bat_and_exe()
        package_check.list_packages()
        package_check.has_prefix()
        package_check.menu_names()
        package_check.no_2to3_pickle()
        package_check.warn_post_link()
        package_check.warn_pyo()
        package_check.pyc_files()
        package_check.no_py_next_so()
        package_check.no_pyc_in_stdlib()
        package_check.no_setuptools()
        package_check.no_easy_install_script()
        package_check.no_pth()
        package_check.check_windows_arch()
        package_check.archive.close()

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
