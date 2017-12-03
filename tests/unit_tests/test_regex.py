import os

import pytest

from conda_verify import checks, utilities


@pytest.fixture
def package_dir():
    return os.path.join(os.path.dirname(__file__), 'test_packages')


@pytest.fixture
def recipe_dir():
    return os.path.join(os.path.dirname(__file__), 'test_recipes')


def test_ver_spec_pat(package_dir, recipe_dir):
    package = os.path.join(package_dir, 'testfile-0.0.30-py27_0.tar.bz2')
    recipe = os.path.join(recipe_dir, 'valid_test_file')
    metadata = utilities.render_metadata(recipe, None)
    package_check = checks.CondaPackageCheck(package)
    recipe_check = checks.CondaRecipeCheck(metadata, recipe)
    package_ver_spec_pat = package_check.ver_spec_pat
    recipe_ver_spec_pat = recipe_check.ver_spec_pat

    extra_spec = '>===3.5'
    ge_version = '>=1.2'
    eq_version = '==1.2.2'
    pin_version = '>=2,<3'
    pin_version_long = '<=2.0.0*,<3.0.0*'
    or_version = '1.0|1.2.*'
    regex_version = '3.6*'
    python_version = '3.6.*'

    assert not utilities.fullmatch(package_ver_spec_pat, extra_spec)
    assert utilities.fullmatch(package_ver_spec_pat, ge_version)
    assert utilities.fullmatch(package_ver_spec_pat, eq_version)
    assert utilities.fullmatch(package_ver_spec_pat, pin_version)
    assert utilities.fullmatch(package_ver_spec_pat, pin_version_long)
    assert utilities.fullmatch(package_ver_spec_pat, or_version)
    assert utilities.fullmatch(package_ver_spec_pat, regex_version)
    assert utilities.fullmatch(package_ver_spec_pat, python_version)

    assert not utilities.fullmatch(recipe_ver_spec_pat, extra_spec)
    assert utilities.fullmatch(recipe_ver_spec_pat, ge_version)
    assert utilities.fullmatch(recipe_ver_spec_pat, eq_version)
    assert utilities.fullmatch(recipe_ver_spec_pat, pin_version)
    assert utilities.fullmatch(recipe_ver_spec_pat, pin_version_long)
    assert utilities.fullmatch(recipe_ver_spec_pat, or_version)
    assert utilities.fullmatch(recipe_ver_spec_pat, regex_version)
    assert utilities.fullmatch(recipe_ver_spec_pat, python_version)
