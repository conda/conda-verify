# -*- coding: utf-8 -*-
from conda_verify.checks import CondaPackageCheck, CondaRecipeCheck


class Verify(object):

    def verify_package(self, path_to_package=None, verbose=True, pedantic=False):
        package_check = CondaPackageCheck(path_to_package, verbose)
        package_check.check_duplicate_members()
        package_check.check_index_encoding()
        package_check.check_members()
        package_check.info_files()
        package_check.no_hardlinks()
        package_check.not_allowed_files(pedantic)
        package_check.index_json()
        package_check.no_bat_and_exe()
        package_check.list_packages()
        package_check.has_prefix(pedantic)
        package_check.menu_names(pedantic)
        package_check.no_2to3_pickle()
        package_check.warn_post_link()
        package_check.warn_pyo()
        package_check.pyc_files()
        package_check.no_py_next_so()
        package_check.no_pyc_in_stdlib()
        package_check.no_setuptools()
        package_check.no_easy_install_script(pedantic)
        package_check.no_pth(pedantic)
        package_check.check_windows_arch()
        package_check.archive.close()

    def verify_recipe(self, rendered_meta=None, recipe_dir=None, pedantic=False):
        recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
        recipe_check.check_fields(pedantic)
        recipe_check.check_source()
        recipe_check.check_requirements()
        recipe_check.validate_files()
        recipe_check.check_about(pedantic)
        recipe_check.check_license_family(pedantic)
        recipe_check.check_dir_content()
