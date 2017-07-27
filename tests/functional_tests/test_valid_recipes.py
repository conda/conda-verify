import os

import pytest

from conda_verify import utilities
from conda_verify.exceptions import RecipeError
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
    except RecipeError as error:
        pytest.fail(error)
