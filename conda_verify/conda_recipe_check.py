import re
import os
from os.path import join, isfile, basename, getsize
from conda_verify.const import LICENSE_FAMILIES, FIELDS
from conda_verify.utils import get_bad_seq, get_field
from conda_verify.exceptions import RecipeError


class CondaRecipeCheck(object):
    def __init__(self, meta, recipe_dir):
        self.meta = meta
        self.recipe_dir = recipe_dir
        self.name_pat = re.compile(r'[a-z0-9_][a-z0-9_\-\.]*$')
        self.version_pat = re.compile(r'[\w\.]+$')
        self.ver_spec_pat = re.compile(r'[\w\.,=!<>\*]+$')
        self.url_pat = re.compile(r'(ftp|http(s)?)://')
        self.hash_pat = {'md5': re.compile(r'[a-f0-9]{32}$'),
            'sha1': re.compile(r'[a-f0-9]{40}$'),
            'sha256': re.compile(r'[a-f0-9]{64}$')}

    def check_fields(self, pedantic=True):
        meta = self.meta
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

    def check_name(self):
        name = get_field(self.meta, "package/name")
        if name:
            name = str(name)
        else:
            raise RecipeError("package name missing")
        if not self.name_pat.match(name) or name.endswith(('.', '-', '_')):
            raise RecipeError("invalid package name '%s'" % name)
        seq = get_bad_seq(name)
        if seq:
            raise RecipeError("'%s' is not allowed in "
                              "package name: '%s'" % (seq, name))

    def check_version(self):
        ver = get_field(self.meta, "package/version")
        if ver:
            ver = str(ver)
        else:
            raise RecipeError("package version missing")
        if not self.version_pat.match(ver):
            raise RecipeError("invalid version '%s'" % ver)
        if ver.startswith(('_', '.')) or ver.endswith(('_', '.')):
            raise RecipeError("version cannot start or end with '_' or '.': %s" %
                              ver)
        seq = get_bad_seq(ver)
        if seq:
            raise RecipeError("'%s' not allowed in version '%s'" % (seq, ver))

    def check_build_number(self):
        bn = get_field(self.meta, "build/number", 0)
        try:
            bn = int(bn)
        except ValueError:
            raise RecipeError("build/number '%s' (not an integer)" % bn)
        if bn < 0:
            raise RecipeError("build/number '%s' (not a positive integer)" % bn)

    def check_requirements(self):
        meta = self.meta
        for req in (get_field(meta, 'requirements/build', []) +
                    get_field(meta, 'requirements/run', [])):
            parts = req.split()
            name = parts[0]
            if not self.name_pat.match(name):
                raise RecipeError("invalid run requirement name '%s'" % name)
            if len(parts) >= 2:
                ver_spec = parts[1]
                if not self.ver_spec_pat.match(ver_spec):
                    raise RecipeError("invalid version spec '%s'" % req)
                if len(parts) == 3 and not self.version_pat.match(ver_spec):
                    raise RecipeError("invalid (pure) version spec '%s'" % req)
            if len(parts) > 3:
                raise RecipeError("invalid spec (too many parts) '%s'" % req)

    def check_url(self, url):
        if not self.url_pat.match(url):
            raise RecipeError("not a valid URL: %s" % url)

    def check_about(self, pedantic=True):
        meta = self.meta
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
                self.check_url(url)
        self.check_license_family(pedantic)

    def check_source(self):
        meta = self.meta
        src = meta.get('source')
        if not src:
            return
        fn = src.get('fn')
        if fn:
            for ht in 'md5', 'sha1', 'sha256':
                hexgigest = src.get(ht)
                if hexgigest and not self.hash_pat[ht].match(hexgigest):
                    raise RecipeError("invalid hash: %s" % hexgigest)
            url = src.get('url')
            if url:
                self.check_url(url)

        git_url = src.get('git_url')
        if git_url and (src.get('git_tag') and src.get('git_branch')):
            raise RecipeError("cannot specify both git_branch and git_tag")

    def check_license_family(self, pedantic=True):
        meta = self.meta
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

    def validate_files(self):
        meta = self.meta
        for field in 'test/files', 'source/patches':
            flst = get_field(meta, field)
            if not flst:
                continue
            for fn in flst:
                if fn.startswith('..'):
                    raise RecipeError("path outsite recipe: %s" % fn)
                path = join(self.recipe_dir, fn)
                if isfile(path):
                    continue
                raise RecipeError("no such file '%s'" % path)

    def check_dir_content(self):
        recipe_dir = self.recipe_dir
        disallowed_extensions = (
            '.tar', '.tar.gz', '.tar.bz2', '.tar.xz',
            '.so', '.dylib', '.la', '.a', '.dll', '.pyd',
        )
        for root, unused_dirs, files in os.walk(recipe_dir):
            for fn in files:
                fn_lower = fn.lower()
                path = join(root, fn)
                # only allow small archives for testing
                if (fn_lower.endswith(('.bz2', '.gz')) and
                            getsize(path) > 512):
                    raise RecipeError("found: %s (too large)" % fn)
                if fn_lower.endswith(disallowed_extensions):
                    raise RecipeError("found: %s" % fn)

        if basename(recipe_dir) == 'icu':
            return

        # check total size od recipe directory (recursively)
        kb_size = self.dir_size(recipe_dir) / 1024
        kb_limit = 512
        if kb_size > kb_limit:
            raise RecipeError("recipe too large: %d KB (limit %d KB)" %
                              (kb_size, kb_limit))

    @staticmethod
    def dir_size(dir_path):
        return sum(sum(getsize(join(root, fn)) for fn in files)
                   for root, unused_dirs, files in os.walk(dir_path))
