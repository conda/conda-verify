# -*- coding: utf-8 -*-
from conda_verify.checks import CondaPackageCheck, CondaRecipeCheck


class Verify(object):

    @staticmethod
    def verify_package(path_to_package=None):
        package_check = CondaPackageCheck(path_to_package)
        package_check.check_duplicate_members()
        package_check.check_index_encoding()
        package_check.check_members()
        package_check.check_info_files()
        package_check.check_for_hardlinks()
        package_check.check_for_unallowed_files()
        package_check.check_index_json()
        package_check.check_for_bat_and_exe()
        package_check.check_prefix_file()
        package_check.check_for_post_links()
        package_check.check_for_egg()
        package_check.check_for_easy_install_script()
        package_check.check_for_pth()
        package_check.check_for_pyo()
        package_check.check_py_next_so()
        package_check.check_for_pyc_in_stdlib()
        package_check.check_for_2to3_pickle()
        package_check.check_pyc_files()
        package_check.check_menu_names()
        package_check.check_windows_arch()
        package_check.check_site_packages()
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
