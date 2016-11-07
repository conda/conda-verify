import re
from os.path import join
from conda_verify.const import LICENSE_FAMILIES, FIELDS
from conda_verify.utils import get_bad_seq, get_field, iter_cfgs
from conda_verify.exceptions import RecipeError


name_pat = re.compile(r'[a-z0-9_][a-z0-9_\-\.]*$')
def check_name(name):
    if name:
        name = str(name)
    else:
        raise RecipeError("package name missing")
    if not name_pat.match(name) or name.endswith(('.', '-', '_')):
        raise RecipeError("invalid package name '%s'" % name)
    seq = get_bad_seq(name)
    if seq:
        raise RecipeError("'%s' is not allowed in "
                          "package name: '%s'" % (seq, name))


version_pat = re.compile(r'[\w\.]+$')
def check_version(ver):
    if ver:
        ver = str(ver)
    else:
        raise RecipeError("package version missing")
    if not version_pat.match(ver):
        raise RecipeError("invalid version '%s'" % ver)
    if ver.startswith(('_', '.')) or ver.endswith(('_', '.')):
        raise RecipeError("version cannot start or end with '_' or '.': %s" %
                          ver)
    seq = get_bad_seq(ver)
    if seq:
        raise RecipeError("'%s' not allowed in version '%s'" % (seq, ver))


def check_build_number(bn):
    if not (isinstance(bn, int) and bn >= 0):
        raise RecipeError("build/number '%s' (not a positive interger)" % bn)


def check_requirements(meta):
    for req in get_field(meta, 'requirements/run', []):
        name = req.split()[0]
        if not name_pat.match(name):
            raise RecipeError("invalid run requirement name '%s'" % name)


def check_license_family(meta, pedantic=True):
    if not pedantic:
        return
    lf = get_field(meta, 'about/license_family',
                   get_field(meta, 'about/license'))
    if lf not in LICENSE_FAMILIES:
        print("""\
Error: license_family is invalid: %s
Note that about/license_family falls back to about/license.
Allowed license families are:""" % lf)
        for x in LICENSE_FAMILIES:
            print("  - %s" % x)
        raise RecipeError("wrong license family")


url_pat = re.compile(r'(ftp|http(s)?)://')
def check_url(url):
    if not url_pat.match(url):
        raise RecipeError("not a valid URL: %s" % url)


def check_about(meta, pedantic=True):
    summary = get_field(meta, 'about/summary')
    if summary and len(summary) > 80:
        msg = "summary exceeds 80 characters"
        if pedantic:
            raise RecipeError(msg)
        else:
            print("Warning: %s" % msg)

    for field in ('about/home', 'about/dev_url', 'about/doc_url',
                  'about/license_url'):
        url = get_field(meta, field)
        if url:
            check_url(url)

    check_license_family(meta)


hash_pat = {'md5': re.compile(r'[a-f0-9]{32}$'),
            'sha1': re.compile(r'[a-f0-9]{40}$'),
            'sha256': re.compile(r'[a-f0-9]{64}$')}
def check_source(meta):
    src = meta.get('source')
    if not src:
        return
    fn = src.get('fn')
    if fn:
        for ht in 'md5', 'sha1', 'sha256':
            hexgigest = src.get(ht)
            if hexgigest and not hash_pat[ht].match(hexgigest):
                raise RecipeError("invalid hash: %s" % hexgigest)
        url = src.get('url')
        if url:
            check_url(url)

    git_url = src.get('git_url')
    if git_url and (src.get('git_tag') and src.get('git_branch')):
        raise RecipeError("cannot specify both git_branch and git_tag")


def validate_meta(meta, pedantic=True):
    for section in meta:
        if section not in FIELDS:
            raise RecipeError("Unknown section: %s" % section)
        submeta = meta.get(section)
        if submeta is None:
            submeta = {}
        for key in submeta:
            if pedantic and key not in FIELDS[section]:
                raise RecipeError("in section %r: unknown key %r" %
                                  (section, key))

    check_name(get_field(meta, 'package/name'))
    check_version(get_field(meta, 'package/version'))
    check_build_number(get_field(meta, 'build/number', 0))
    check_requirements(meta)
    check_about(meta)
    check_source(meta)
    check_license_family(meta, pedantic)
    check_about(meta, pedantic)


def verify(rendered_meta=None, recipe_dir=None, **kwargs):
    meta_path = join(recipe_dir, 'meta.yaml')
    for cfg in iter_cfgs():
        pedantic = kwargs.get("pedantic") if "pedantic" in kwargs.keys() else True
        validate_meta(rendered_meta, pedantic)

