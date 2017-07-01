from conda_verify.conda_package_check import CondaPackageCheck


def verify_files(path_to_package=None, verbose=True, **kwargs):
    pedantic = kwargs.get("pedantic") if "pedantic" in kwargs.keys() else True
    package_check = CondaPackageCheck(path_to_package, verbose)
    # package_check.check_members()
    package_check.info_files()
    package_check.no_hardlinks()
    package_check.not_allowed_files(pedantic=pedantic)
    package_check.index_json()
    package_check.no_bat_and_exe()
    package_check.list_packages()
    package_check.has_prefix(pedantic=pedantic)
    package_check.menu_names(pedantic=pedantic)

    package_check.t.close()
