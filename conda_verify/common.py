import re
from collections import defaultdict

from anaconda_verify.utils import get_bad_seq


name_pat = re.compile(r'[a-z0-9_][a-z0-9_\-\.]*$')
def check_name(name):
    if not name:
        return "package name missing"
    name = str(name)
    if not name_pat.match(name) or name.endswith(('.', '-', '_')):
        return "invalid package name '%s'" % name
    seq = get_bad_seq(name)
    if seq:
        return "'%s' is not allowed in package name: '%s'" % (seq, name)
    return None


version_pat = re.compile(r'[\w\.]+$')
def check_version(ver):
    if not ver:
        return "package version missing"
    ver = str(ver)
    if not version_pat.match(ver):
        return "invalid version '%s'" % ver
    if ver.startswith(('_', '.')) or ver.endswith(('_', '.')):
        return "version cannot start or end with '_' or '.': %s" % ver
    seq = get_bad_seq(ver)
    if seq:
        return "'%s' not allowed in version '%s'" % (seq, ver)
    return None


hash_pat = re.compile(r'[gh][0-9a-f]{5,}', re.I)
def check_build_string(build):
    build = str(build)
    if not version_pat.match(build):
        return "invalid build string '%s'" % build
    if hash_pat.search(build):
        return "hashes not allowed in build string '%s'" % build
    return None


ver_spec_pat = re.compile(r'[\w\.,=!<>\*]+$')
def check_spec(spec):
    if not spec:
        return "spec missing"
    spec = str(spec)
    parts = spec.split()
    nparts = len(parts)
    if nparts == 0:
        return "empty spec '%s'" % spec
    if not name_pat.match(parts[0]):
        return "invalid name spec '%s'" % spec
    if nparts >= 2 and not ver_spec_pat.match(parts[1]):
        return "invalid version spec '%s'" % spec
    if nparts == 3 and not version_pat.match(parts[1]):
        return "invalid (pure) version spec '%s'" % spec
    if len(parts) > 3:
        return "invalid spec (too many parts) '%s'" % spec
    return None


def check_specs(specs):
    name_specs = defaultdict(list)
    for spec in specs:
        res = check_spec(spec)
        if res:
            return res
        name_specs[spec.split()[0]].append(spec)
    for name in name_specs:
        specs = name_specs[name]
        if len(specs) > 1:
            return "duplicate specs: %s" % specs
    return None


def check_build_number(bn):
    if not (isinstance(bn, int) and bn >= 0):
        return "build number '%s' (not a positive interger)" % bn


def get_python_version_specs(specs):
    """
    Return the Python version (as a string "x.y") from a given list of specs.
    If Python is not a dependency, or if the version does not start with x.y,
    None is returned
    """
    pat = re.compile(r'(\d\.\d)')
    for spec in specs:
        spec = str(spec)
        parts = spec.split()
        nparts = len(parts)
        if nparts < 2:
            continue
        name, version = parts[:2]
        if name != 'python':
            continue
        m = pat.match(version)
        if m:
            return m.group(1)
    return None


if __name__ == '__main__':
    import sys
    print(check_spec('numpy 1.2'))
    print(check_build_number(3))
    #print(get_python_version_specs(sys.argv[1:]))
    print(sys.argv[1])
    print(check_build_string(sys.argv[1]))