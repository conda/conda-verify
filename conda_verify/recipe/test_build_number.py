from conda_verify.conda_recipe_check import CondaRecipeCheck


def verify_build_number(rendered_meta=None, recipe_dir=None, **kwargs):
    recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
