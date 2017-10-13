import os

import pytest

from conda_verify import utilities
from conda_verify.verify import Verify


@pytest.fixture
def recipe_dir():
    return os.path.join(os.path.dirname(__file__), 'test_recipes')


@pytest.fixture
def verifier():
    recipe_verifier = Verify()
    return recipe_verifier


def test_valid_test_file(recipe_dir, verifier):
    recipe = os.path.join(recipe_dir, 'valid_test_file')
    metadata = utilities.render_metadata(recipe, None)

    try:
        verifier.verify_recipe(rendered_meta=metadata, recipe_dir=recipe)
    except SystemExit as error:
        pytest.fail(error)


def test_passing_legacy_arguments_to_recipe_shows_warning(recipe_dir, verifier, caplog):
    recipe = os.path.join(recipe_dir, 'valid_test_file')
    metadata = utilities.render_metadata(recipe, None)

    verifier.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, run_scripts=None,
                           ignore_scripts=None)
    assert caplog.text.count('Ignoring legacy ignore_scripts or run_scripts.') == 0
    verifier.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, run_scripts='abc.py')
    assert caplog.text.count('Ignoring legacy ignore_scripts or run_scripts.') == 1
    verifier.verify_recipe(rendered_meta=metadata, recipe_dir=recipe, ignore_scripts='abc.py')
    # actually only one more, but we still have the earlier one in the pipe, too.
    assert caplog.text.count('Ignoring legacy ignore_scripts or run_scripts.') == 2
