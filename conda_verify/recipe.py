import os
import re
import sys
import json
from os.path import isfile, join

import yaml

from utils import memoized


VERBOSE = False

FIELDS = {
    'package': {'name', 'version'},
    'source': {'fn', 'url', 'md5', 'sha1', 'sha256',
               'git_url', 'git_tag', 'git_branch',
               'patches', 'hg_url', 'hg_tag'},
    'build': {'features', 'track_features',
              'number', 'entry_points', 'osx_is_app',
              'preserve_egg_dir', 'win_has_prefix', 'no_link',
              'ignore_prefix_files', 'msvc_compiler',
              'detect_binary_files_with_prefix',
              'always_include_files'},
    'requirements': {'build', 'run'},
    'app': {'entry', 'icon', 'summary', 'type', 'cli_opts'},
    'test': {'requires', 'commands', 'files', 'imports'},
    'about': {'home', 'license', 'license_family', 'license_file',
              'summary', 'description', 'doc_url', 'dev_url'},
}

ALLOWED_LICENSE_FAMILIES = set("""
AGPL
GPL2
GPL3
LGPL
BSD
MIT
Apache
PSF
Public-Domain
Proprietary
Other
""".split())


vxy_pat = re.compile(r'(\d+)\.(\d+)')
feat_pat = re.compile(r'(vc\d+|nomkl|debug)$')


def ns_cfg(cfg):
    plat = cfg['plat']
    py = cfg['PY']
    np = cfg['NPY']
    for x in py, np:
        assert isinstance(x, int), x
    return dict(
        nomkl = bool(cfg['NOMKL']),
        debug = bool(cfg['DEBUG']),
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
        sys.exit("Error: package name missing")
    if not name_pat.match(name):
        sys.exit("Error: invalid package name '%s'" % name)


version_pat = re.compile(r'[\w\.]+$')
def check_version(ver):
    if ver:
        ver = str(ver)
    else:
        sys.exit("Error: package version missing")
    if not version_pat.match(ver):
        sys.exit("Error: invalid package version '%s'" % ver)


def check_build_number(bn):
    if not (isinstance(bn, int) and bn >= 0):
        sys.exit("Error: build/number '%s' (not a positive interger)" % bn)


def check_license_family(meta):
    lf = get_field(meta, 'about/license_family',
                   get_field(meta, 'about/license'))
    if lf not in ALLOWED_LICENSE_FAMILIES:
        print("""\
Error: license_family is invalid: %s
Note that about/license_family falls back to about/license.
Allowed license families are:""" % lf)
        for x in ALLOWED_LICENSE_FAMILIES:
            print("  - %s" % x)
        exit(1)


url_pat = re.compile(r'(ftp|http(s)?)://')
def check_url(url):
    if not url_pat.match(url):
        sys.exit("Error: not a valid URL: %s" % url)


def check_about(meta):
    summary = get_field(meta, 'about/summary')
    if summary and len(summary) > 80:
        sys.exit("Error: summary exceeds 80 characters")

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
                sys.exit("Error: invalid hash: %s" % hexgigest)
        url = src.get('url')
        if url:
            check_url(url)

    git_url = src.get('git_url')
    if git_url and (src.get('git_tag') and src.get('git_branch')):
        sys.exit("Error: cannot specify both git_branch and git_tag")


lic_pat = re.compile(r'.+?\s+\(http\S+\)$')

def validate_meta(meta):
    for section in meta:
        if section not in FIELDS:
            sys.exit("Unknown section: %s" % section)
        submeta = meta.get(section)
        if submeta is None:
            submeta = {}
        for key in submeta:
            if key not in FIELDS[section]:
                sys.exit("In section %r: unknown key %r" % (section, key))

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
                sys.exit("Error: path outsite recipe: %s" % fn)
            path = join(recipe_dir, fn)
            if isfile(path):
               continue
            sys.exit("Error: no such file '%s'" % path)


def iter_cfgs():
    for py in 27, 34, 35:
        for plat in 'linux-64', 'linux-32', 'osx-64', 'win-32', 'win-64':
            yield dict(plat=plat, PY=py, NPY=111, NOMKL=0, DEBUG=0)


def validate_recipe(recipe_dir):
    for fn in os.listdir(recipe_dir):
        # ensure .json files can be parsed
        if fn.endswith('.json'):
            json.load(open(join(recipe_dir, fn)))

    meta_path = join(recipe_dir, 'meta.yaml')
    data = open(meta_path, 'rb').read()
    for c in data:
        n = ord(c)
        if not (n == 10 or 32 <= n < 127):
            sys.exit("Error: non-ASCII character '%s' found in %s" %
                     (c, meta_path))
    if '{{' in data:
        sys.exit("Error: found {{ in %s (Jinja templating not allowed)" %
                 meta_path)

    for cfg in iter_cfgs():
        meta = parse(data, cfg)
        validate_meta(meta)
        validate_files(recipe_dir, meta)
