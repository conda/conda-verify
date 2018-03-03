import os

from click.testing import CliRunner
import pytest

from conda_verify.cli import cli


@pytest.fixture
def package_dir():
    return os.path.join(os.path.dirname(__file__), 'test_packages')


@pytest.fixture
def recipe_dir():
    return os.path.join(os.path.dirname(__file__), 'test_recipes')


def test_package_cli(package_dir):
    package = os.path.join(package_dir, 'testfile-0.0.30-py27_0.tar.bz2')
    runner = CliRunner()
    result = runner.invoke(cli, [package])
    assert not result.exception
    assert 'Verifying {}...' .format(package) in result.output


def test_recipe_cli(recipe_dir):
    recipe = os.path.join(recipe_dir, 'valid_test_file')
    runner = CliRunner()
    result = runner.invoke(cli, [recipe])
    assert not result.exception
    assert 'Verifying {}' .format(recipe) in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert 'conda-verify, version 3.0.2' in result.output
