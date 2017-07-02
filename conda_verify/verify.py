# -*- coding: utf-8 -*-
from conda_verify.package import (verify_package_files, verify_2to3, verify_post_link,
                                  verify_pyc, verify_setup_files, verify_arch)

from conda_verify.recipe import (verify_fields, verify_source, verify_requirements,
                                 verify_about, verify_license_family, verify_files)


class Verify(object):
    def __init__(self):
        pass

    def verify_recipe(self, run_scripts=None, ignore_scripts=None, **kwargs):
        verify_fields(**kwargs)
        verify_source(**kwargs)
        verify_requirements(**kwargs)
        verify_about(**kwargs)
        verify_license_family(**kwargs)
        verify_files(**kwargs)

    def verify_package(self, run_scripts=None, ignore_scripts=None, **kwargs):
        verify_package_files(**kwargs)
        verify_2to3(**kwargs)
        verify_post_link(**kwargs)
        verify_pyc(**kwargs)
        verify_setup_files(**kwargs)
        verify_arch(**kwargs)
