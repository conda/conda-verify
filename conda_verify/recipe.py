from conda_verify.conda_recipe_check import CondaRecipeCheck


def verify_about(rendered_meta=None, recipe_dir=None, **kwargs):
    recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
    pedantic = kwargs.get("pedantic") if "pedantic" in kwargs.keys() else True
    recipe_check.check_about(pedantic)


def verify_fields(rendered_meta=None, recipe_dir=None, **kwargs):
    recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
    pedantic = kwargs.get("pedantic") if "pedantic" in kwargs.keys() else True
    recipe_check.check_fields(pedantic)


def verify_license_family(rendered_meta=None, recipe_dir=None, **kwargs):
    recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
    pedantic = kwargs.get("pedantic") if "pedantic" in kwargs.keys() else True
    recipe_check.check_license_family(pedantic)


def verify_files(rendered_meta=None, recipe_dir=None, **kwargs):
    recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
    recipe_check.validate_files()
    recipe_check.check_dir_content()


def verify_requirements(rendered_meta=None, recipe_dir=None, **kwargs):
    recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
    recipe_check.check_requirements()


def verify_source(rendered_meta=None, recipe_dir=None, **kwargs):
    recipe_check = CondaRecipeCheck(rendered_meta, recipe_dir)
    recipe_check.check_source()
