from conda_verify.conda_recipe_check import CondaRecipeCheck


def verify_license_family(rendered_meta=None, recipe_dir=None, **kwargs):
    recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
    pedantic = kwargs.get("pedantic") if "pedantic" in kwargs.keys() else True
    recipe_check.check_license_family(pedantic)