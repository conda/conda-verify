import os

import pytest

from conda_verify import utils
from conda_verify.exceptions import RecipeError
from conda_verify.verify import Verify


@pytest.fixture
def recipe_dir():
    return os.path.join(os.path.dirname(__file__), 'test_recipes')


@pytest.fixture
def verifier():
    recipe_verifier = Verify()
    return recipe_verifier


def test_invalid_package_field(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_package_field')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'Unknown section: extra_field' in str(excinfo))


def test_invalid_package_field_key(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_package_field_key')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "in section 'package': unknown key" in str(excinfo))


def test_invalid_source_field_key(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_source_field_key')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "in section 'source': unknown key" in str(excinfo))


def test_invalid_build_field_key(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_build_field_key')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "in section 'build': unknown key" in str(excinfo))


def test_invalid_requirements_field_key(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_requirements_field_key')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "in section 'requirements': unknown key" in str(excinfo))


def test_invalid_test_field_key(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_test_field_key')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "in section 'test': unknown key" in str(excinfo))


def test_invalid_about_field_key(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_about_field_key')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "in section 'about': unknown key" in str(excinfo))


def test_invalid_app_field_key(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_app_field_key')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "in section 'app': unknown key" in str(excinfo))


def test_invalid_extra_field_key(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_extra_field_key')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "in section 'extra': unknown key" in str(excinfo))


def test_no_package_name(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'no_package_name')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'package name missing' in str(excinfo))


def test_invalid_package_name(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_package_name')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'invalid package name' in str(excinfo))


def test_invalid_package_sequence(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_package_sequence')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "'_-' is not allowed" in str(excinfo))


def test_no_package_version(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'no_package_version')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'package version missing' in str(excinfo))


def test_invalid_package_version(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_package_version')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'invalid version' in str(excinfo))


def test_invalid_package_version_prefix(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_package_version_prefix')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "version cannot start or end with '_' or '.'" in str(excinfo))


def test_invalid_package_version_sequence(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_package_version_sequence')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "'._' not allowed in" in str(excinfo))


def test_invalid_build_number(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_build_number')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "build/number 'a' (not a positive integer)" in str(excinfo))


def test_invalid_build_number_negative(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_build_number_negative')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "build/number '-1' (not a positive integer)" in str(excinfo))


def test_invalid_build_requirement_name(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_build_requirement_name')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "invalid build requirement name 'python!'" in str(excinfo))


def test_invalid_build_requirement_version_specification(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir,
                          'invalid_build_requirement_version_specification')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "invalid (pure) version spec 'python >= 2.7" in str(excinfo))


def test_invalid_run_requirement_version_specification(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir,
                          'invalid_run_requirement_version_specification')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "invalid version spec 'python \\>='" in str(excinfo))


def test_invalid_run_requirement_name(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_run_requirement_name')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "invalid run requirement name 'python@#'" in str(excinfo))


def test_invalid_source_url(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_source_url')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ("conda_verify.exceptions.RecipeError: "
            "not a valid URL: www.continuum.io" in str(excinfo))


def test_invalid_about_summary(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_about_summary')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'summary exceeds 80 characters' in str(excinfo))


def test_invalid_about_summary_message(recipe_dir, verifier, capfd):
    recipe = os.path.join(recipe_dir, 'invalid_about_summary')
    metadata = utils.render_metadata(recipe, None)

    verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                           recipe_dir=recipe)

    output, error = capfd.readouterr()

    assert ('Warning: summary exceeds 80 characters' in str(output))


def test_invalid_about_url(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_about_url')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'not a valid URL: www.continuum.io' in str(excinfo))


def test_invalid_source_hash(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_source_hash')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'invalid hash' in str(excinfo))


def test_invalid_source_giturl(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_source_giturl')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'cannot specify both git_branch and git_tag' in str(excinfo))


def test_invalid_license_family(recipe_dir, verifier, capfd):
    recipe = os.path.join(recipe_dir, 'invalid_license_family')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=True, rendered_meta=metadata,
                               recipe_dir=recipe)

    output, error = capfd.readouterr()

    assert ('conda_verify.exceptions.RecipeError: '
            'wrong license family' in str(excinfo))

    assert 'Allowed license families are:' in output


def test_invalid_test_files(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_test_files')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'no such file' in str(excinfo))


def test_invalid_test_file_path(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_test_file_path')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'path outsite recipe: ../test-data.txt' in str(excinfo))


def test_invalid_dir_size(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_dir_size')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'recipe too large: 1006 KB (limit 512 KB)' in str(excinfo))


def test_invalid_dir_content(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_dir_content')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'found: testfile.so' in str(excinfo))


def test_invalid_dir_content_filesize(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'invalid_dir_content_filesize')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert ('conda_verify.exceptions.RecipeError: '
            'found: test.tar.bz2 (too large)' in str(excinfo))


def test_duplicate_version_specifications(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'duplicate_version_specs')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert "duplicate specs: ['python', 'python']" in str(excinfo)


def test_missing_version_specifications(recipe_dir, verifier, capfd):
    recipe = os.path.join(recipe_dir, 'missing_version_specs')
    metadata = utils.render_metadata(recipe, None)

    verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                           recipe_dir=recipe)

    output, error = capfd.readouterr()

    assert "empty spec" in str(output)


def test_many_version_specifications(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'many_version_specs')
    metadata = utils.render_metadata(recipe, None)

    with pytest.raises(RecipeError) as excinfo:
        verifier.verify_recipe(pedantic=False, rendered_meta=metadata,
                               recipe_dir=recipe)

    assert "invalid spec (too many parts) 'python 3.6 * 2 * 3" in str(excinfo)
