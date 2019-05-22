import os

import pytest

from conda_verify import utilities
from conda_verify.verify import Verify
from conda_verify.errors import RecipeError


@pytest.fixture
def recipe_dir():
    return os.path.join(os.path.dirname(__file__), 'test_recipes')


def test_invalid_package_field(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_package_field')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2109] Found invalid section "extra_field"' in error


def test_invalid_package_field_key(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_package_field_key')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2110] Found invalid field "extra" in section "package"' in error


def test_invalid_source_field_key(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_source_field_key')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2110] Found invalid field "sha3" in section "source"' in error


def test_invalid_multiple_source_field_key(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_multiple_sources')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2110] Found invalid field "gti_url" in section "source"' in error


def test_invalid_build_field_key(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_build_field_key')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2110] Found invalid field "yesarch" in section "build"' in error


def test_invalid_requirements_field_key(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_requirements_field_key')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2110] Found invalid field "extra_field" in section "requirements"' in error


def test_invalid_test_field_key(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_test_field_key')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2110] Found invalid field "no_files" in section "test"' in error


def test_invalid_about_field_key(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_about_field_key')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata,
                               recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2110] Found invalid field "something_extra" in section "about"' in error


def test_invalid_app_field_key(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_app_field_key')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2110] Found invalid field "noentry" in section "app"' in error


def test_invalid_package_name(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_package_name')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2102] Found invalid package name "some_package." in meta.yaml' in error


def test_invalid_package_sequence(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_package_sequence')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2103] Found invalid sequence "_-" in package name' in error


def test_no_package_version(recipe_dir):
    recipe = os.path.join(recipe_dir, 'no_package_version')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2104] Missing package version in meta.yaml' in error


def test_invalid_package_version(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_package_version')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2105] Found invalid package version "1.0.0rc3!" in meta.yaml' in error


def test_invalid_package_version_prefix(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_package_version_prefix')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2105] Found invalid package version "_1.0.0rc3" in meta.yaml' in error


def test_invalid_package_version_sequence(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_package_version_sequence')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2106] Found invalid sequence "._" in package version' in error


def test_invalid_build_number(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_build_number')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2107] Build number in info/index.json must be an integer' in error


def test_invalid_build_number_negative(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_build_number_negative')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2108] Build number in info/index.json cannot be a negative integer' in error


def test_invalid_source_url(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_source_url')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2120] Found invalid URL "www.continuum.io" in meta.yaml' in error


def test_invalid_about_summary(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_about_summary')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2117] Found summary with length greater than 80 characters' in error


def test_invalid_about_url(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_about_url')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2118] Found invalid URL "www.continuum.io" in meta.yaml' in error


def test_invalid_source_hash(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_source_hash')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2119] Found invalid hash "abc123" in meta.yaml' in error


def test_invalid_license_family(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_license_family')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2122] Found invalid license family "The Extra License"' in error


def test_invalid_test_files(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_test_files')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2124] Found file "test-data.txt" in meta.yaml that doesn\'t exist' in error


def test_invalid_test_file_path(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_test_file_path')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2123] Found file "../test-data.txt" listed outside recipe directory' in error


def test_invalid_dir_content(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_dir_content')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert any('[C2125] Found disallowed file with extension' in e for e in error)
    assert any('testfile.tar' in e for e in error)


def test_invalid_dir_content_filesize(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_dir_content_filesize')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert any('[C2125] Found disallowed file with extension' in e for e in error)
    assert any('test.tar.bz2' in e for e in error)


def test_duplicate_version_specifications(recipe_dir):
    recipe = os.path.join(recipe_dir, 'duplicate_version_specs')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert "[C2116] Found duplicate run requirements: ['python', 'python']" in error


def test_conda_forge_example_recipe(recipe_dir):
    recipe = os.path.join(recipe_dir, 'conda_forge')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2126] Found conda-forge comment in meta.yaml file' in error


def test_invalid_outputs(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_output')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2110] Found invalid field "srcitp" in section "outputs"' in error


@pytest.mark.skipif(os.getenv('CONDA_BUILD') == '1',
    reason='conda build handles invalid sources at runtime')
def test_invalid_sources(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_sources')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2121] Found both git_branch and git_tag in meta.yaml source field' in error


def test_duplicate_build_requirements(recipe_dir):
    recipe = os.path.join(recipe_dir, 'duplicate_build_requirements')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert ("[C2115] Found duplicate build requirements: ['python', 'python']" in error or
            "[C2115] Found duplicate build requirements: ['python 3.6.*', 'python 3.6.*']" in error)


@pytest.mark.skipif(os.getenv('CONDA_BUILD') == '1',
    reason='conda build handles invalid characters at runtime')
def test_invalid_build_requirement_name(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_build_requirement_name')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2111] Found invalid build requirement "python!"' in error


@pytest.mark.skipif(os.getenv('CONDA_BUILD') == '1',
    reason='conda build handles invalid requirement versions at runtime')
def test_invalid_build_requirement_version(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_build_requirement_version')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2114] Found invalid dependency "setuptools >= 3.4 < 3045" in meta.yaml' in error


@pytest.mark.skipif(os.getenv('CONDA_BUILD') == '1',
    reason='conda build handles invalid characters at runtime')
def test_invalid_run_requirement_name(recipe_dir):
    recipe = os.path.join(recipe_dir, 'invalid_run_requirement_name')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2112] Found invalid run requirement "python@#"' in error


@pytest.mark.skipif(os.getenv('CONDA_BUILD') == '1',
    reason='conda build handles missing package names at runtime')
def test_no_package_name(recipe_dir):
    recipe = os.path.join(recipe_dir, 'no_package_name')
    metadata = utilities.render_metadata(recipe, None)

    with pytest.raises(RecipeError):
        Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=True)

    package, error = Verify.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, exit_on_error=False)

    assert '[C2101] Missing package name in meta.yaml' in error
