import re
import sys

import jinja2
import yaml
from six import string_types

import future.builtins

from conda_verify.constants import MAGIC_HEADERS, DLL_TYPES

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


@lru_cache(maxsize=32)
def yamlize(data):
    res = yaml.load(data)
    # ensure the result is a dict
    if res is None:
        res = {}
    return res


def ns_cfg(cfg):
    plat = '-'.join((cfg['platform'], cfg['arch']))
    py = int(''.join(cfg['python'].split('.')))
    np = int(''.join(cfg['numpy'].split('.')))

    return dict(
        nomkl=False,
        debug=False,
        linux=plat.startswith('linux-'),
        linux32=bool(plat == 'linux-32'),
        linux64=bool(plat == 'linux-64'),
        armv7l=bool(plat == 'linux-armv7l'),
        arm=bool(plat == 'linux-armv7l'),
        ppc64le=bool(plat == 'linux-ppc64le'),
        osx=plat.startswith('osx-'),
        unix=plat.startswith(('linux-', 'osx-')),
        win=plat.startswith('win-'),
        win32=bool(plat == 'win-32'),
        win64=bool(plat == 'win-64'),
        x86=plat.endswith(('-32', '-64')),
        x86_64=plat.endswith('-64'),
        py=py,
        py3k=bool(30 <= py < 40),
        py2k=bool(20 <= py < 30),
        py26=bool(py == 26),
        py27=bool(py == 27),
        py33=bool(py == 33),
        py34=bool(py == 34),
        py35=bool(py == 35),
        py36=bool(py == 36),
        np=np,
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


def parse(data, cfg):
    if cfg is not None:
        data = select_lines(data, ns_cfg(cfg))
    # ensure we create new object, because yamlize is memoized
    return dict(yamlize(data))


def render_jinja2(recipe_dir):
    loaders = [jinja2.FileSystemLoader(recipe_dir)]
    env = jinja2.Environment(loader=jinja2.ChoiceLoader(loaders))
    template = env.get_or_select_template('meta.yaml')
    return template.render(environment=env)


try:
    # circular dependency.  We only try this import so that conda-build is an optional
    #      conda-verify dep
    from conda_build import api

    def render_metadata(recipe_dir, cfg):
        m = api.render(recipe_dir, finalize=False, bypass_env_check=True,
                       **(cfg if cfg else {}))[0][0]
        return m.get_rendered_recipe_text()
except ImportError:
    def render_metadata(recipe_dir, cfg):
        data = render_jinja2(recipe_dir)
        return parse(data, cfg)


def iter_cfgs():
    for py in "27", "34", "35":
        for plat in 'linux-64', 'linux-32', 'osx-64', 'win-32', 'win-64':
            platform, arch = plat.split('-')
            yield dict(platform=platform, arch=arch, python=py, numpy="1.11")


def get_object_type(data):
    head = data[:4]
    if head not in MAGIC_HEADERS:
        return None
    lookup = MAGIC_HEADERS.get(head)
    if lookup == 'DLL':
        pos = data.find(b'PE\0\0')
        if pos < 0:
            return "<no PE header found>"
        data = future.builtins.bytes(data)
        i = data[pos + 4] + 256 * data[pos + 5]
        return "DLL " + DLL_TYPES.get(i)
    elif lookup.startswith('MachO'):
        return lookup
    elif lookup == 'ELF':
        return "ELF" + {'\x01': '32', '\x02': '64'}.get(data[4])


def get_bad_seq(s):
    for seq in ('--', '-.', '-_',
                '.-', '..', '._',
                '_-', '_.'):  # but '__' is fine
        if seq in s:
            return seq
    return None


def all_ascii(data, allow_CR=False):
    newline = [10]  # LF
    if allow_CR:
        newline.append(13)  # CR
    for c in data:
        n = ord(c) if sys.version_info[0] == 2 else c
        if not (n in newline or 32 <= n < 127):
            return False
    return True


def ensure_list(argument):
    if isinstance(argument, list):
        return argument
    elif isinstance(argument, string_types):
        return argument.split(',')
    return [argument]


def fullmatch(regex, string, flags=0):
    """Emulate python-3.4 re.fullmatch().

    Credit: https://stackoverflow.com/questions/30212413/
    """
    return re.match("(?:" + regex + r")\Z", string, flags=flags)
