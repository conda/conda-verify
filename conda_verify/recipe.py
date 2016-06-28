from __future__ import print_function, division, absolute_import

import re
from os.path import isfile, join

import yaml

from conda_verify.const import LICENSE_FAMILIES, FIELDS
from conda_verify.utils import memoized



def ns_cfg(cfg):
    plat = cfg['plat']
    py = cfg['PY']
    np = cfg['NPY']
    for x in py, np:
        assert isinstance(x, int), x
    return dict(
        nomkl = False,
        debug = False,
        linux = plat.startswith('linux-'),
        linux32 = bool(plat == 'linux-32'),
        linux64 = bool(plat == 'linux-64'),
        armv7l = False,
        arm = False,
        ppc64le = False,
        osx = plat.startswith('osx-'),
        unix = plat.startswith(('linux-', 'osx-')),
        win = plat.startswith('win-'),
        win32 = bool(plat == 'win-32'),
        win64 = bool(plat == 'win-64'),
        x86 = plat.endswith(('-32', '-64')),
        x86_64 = plat.endswith('-64'),
        py = py,
        py3k = bool(30 <= py < 40),
        py2k = bool(20 <= py < 30),
        py26 = bool(py == 26),
        py27 = bool(py == 27),
        py33 = bool(py == 33),
        py34 = bool(py == 34),
        py35 = bool(py == 35),
        np = np,
    )


sel_pat = re.compile(r'(.+?)\s*\[(.+)\]$')
def select_lines(data, namespace):
    lines = []
    for line in data.splitlines():
        line = line.rstrip()
        m = sel_pat.match(line)
        if m:
            cond = m.group(2)
            if eval(cond, namespace, {}):
                lines.append(m.group(1))
            continue
        lines.append(line)
    return '\n'.join(lines) + '\n'


@memoized
def yamlize(data):
    res = yaml.load(data)
    # ensure the result is a dict
    if res is None:
        res = {}
    return res


def parse(data, cfg):
    if cfg is not None:
        data = select_lines(data, ns_cfg(cfg))
    # ensure we create new object, because yamlize is memoized
    return dict(yamlize(data))


def get_field(meta, field, default=None):
    section, key = field.split('/')
    submeta = meta.get(section)
    if submeta is None:
        submeta = {}
    return submeta.get(key, default)


name_pat = re.compile(r'[a-z0-9_][a-z0-9_\-\.]*$')
def check_name(name):
    if name:
        name = str(name)
    else:
        raise Exception("package name missing")
    if not name_pat.match(name):
        raise Exception("invalid package name '%s'" % name)


version_pat = re.compile(r'[\w\.]+$')
def check_version(ver):
    if ver:
        ver = str(ver)
    else:
        raise Exception("package version missing")
    if not version_pat.match(ver):
        raise Exception("invalid package version '%s'" % ver)


def check_build_number(bn):
    if not (isinstance(bn, int) and bn >= 0):
        raise Exception("build/number '%s' (not a positive interger)" % bn)


def check_license_family(meta):
    lf = get_field(meta, 'about/license_family',
                   get_field(meta, 'about/license'))
    if lf not in LICENSE_FAMILIES:
        print("""\
Error: license_family is invalid: %s
Note that about/license_family falls back to about/license.
Allowed license families are:""" % lf)
        for x in LICENSE_FAMILIES:
            print("  - %s" % x)
        exit(1)


url_pat = re.compile(r'(ftp|http(s)?)://')
def check_url(url):
    if not url_pat.match(url):
        raise Exception("not a valid URL: %s" % url)


def check_about(meta):
    summary = get_field(meta, 'about/summary')
    if summary and len(summary) > 80:
        raise Exception("summary exceeds 80 characters")

    for field in 'about/home', 'about/dev_url', 'about/doc_url':
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
                raise Exception("invalid hash: %s" % hexgigest)
        url = src.get('url')
        if url:
            check_url(url)

    git_url = src.get('git_url')
    if git_url and (src.get('git_tag') and src.get('git_branch')):
        raise Exception("cannot specify both git_branch and git_tag")


lic_pat = re.compile(r'.+?\s+\(http\S+\)$')

def validate_meta(meta):
    for section in meta:
        if section not in FIELDS:
            raise Exception("Unknown section: %s" % section)
        submeta = meta.get(section)
        if submeta is None:
            submeta = {}
        for key in submeta:
            if key not in FIELDS[section]:
                raise Exception("in section %r: unknown key %r" %
                                (section, key))

    check_name(get_field(meta, 'package/name'))
    check_version(get_field(meta, 'package/version'))
    check_build_number(get_field(meta, 'build/number', 0))
    check_about(meta)
    check_source(meta)

    lic = get_field(meta, 'about/license')
    if lic and lic.endswith(')'):
        assert lic_pat.match(lic), lic


def validate_files(recipe_dir, meta):
    for field in 'test/files', 'source/patches':
        flst = get_field(meta, field)
        if not flst:
            continue
        for fn in flst:
            if fn.startswith('..'):
                raise Exception("path outsite recipe: %s" % fn)
            path = join(recipe_dir, fn)
            if isfile(path):
               continue
            raise Exception("no such file '%s'" % path)


def iter_cfgs():
    for py in 27, 34, 35:
        for plat in 'linux-64', 'linux-32', 'osx-64', 'win-32', 'win-64':
            yield dict(plat=plat, PY=py, NPY=111)


def validate_recipe(recipe_dir):
    meta_path = join(recipe_dir, 'meta.yaml')
    with open(meta_path) as fi:
        data = fi.read()
    for c in data:
        n = ord(c)
        if not (n == 10 or 32 <= n < 127):
            raise Exception("non-ASCII character '%s' found in %s" %
                            (c, meta_path))
    if '{{' in data:
        raise Exception("found {{ in %s (Jinja templating not allowed)" %
                        meta_path)

    for cfg in iter_cfgs():
        meta = parse(data, cfg)
        validate_meta(meta)
        validate_files(recipe_dir, meta)
