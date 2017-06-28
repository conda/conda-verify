from conda_verify.conda_recipe_check import CondaRecipeCheck


def verify_files(rendered_meta=None, recipe_dir=None, **kwargs):
    recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
    recipe_check.validate_files()
    recipe_check.check_dir_content()
