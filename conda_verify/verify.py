# -*- coding: utf-8 -*-
from conda_verify.package import (test_files, test_no_2to3_pickle,
                                  test_no_post_link, test_no_pyc_pyo,
                                  test_setup_files, test_windows_arch)

from conda_verify.recipe import (test_about, test_build_number, test_fields,
                                 test_recipe_files, test_license_family,
                                 test_package, test_requirements, test_source)


class Verify(object):
    def __init__(self):
        pass

    def verify_recipe(self, run_scripts=None, ignore_scripts=None, **kwargs):
        test_fields.verify_fields(**kwargs)
        test_package.verify_package_info(**kwargs)
        test_source.verify_source(**kwargs)
        test_build_number.verify_build_number(**kwargs)
        test_requirements.verify_requirements(**kwargs)
        test_about.verify_about(**kwargs)
        test_license_family.verify_license_family(**kwargs)
        test_recipe_files.verify_files(**kwargs)

    def verify_package(self, run_scripts=None, ignore_scripts=None, **kwargs):
        test_files.verify_files(**kwargs)
        test_no_2to3_pickle.verify_2to3(**kwargs)
        test_no_post_link.verify_post_link(**kwargs)
        test_no_pyc_pyo.verify_pyc(**kwargs)
        test_setup_files.verify_setup_files(**kwargs)
        test_windows_arch.verify_arch(**kwargs)
