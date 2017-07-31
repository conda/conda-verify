import json
import os
import re
import sys
import tarfile

from conda_verify.errors import Error, PackageError
from conda_verify.constants import FIELDS, LICENSE_FAMILIES
from conda_verify.utilities import all_ascii, get_bad_seq, get_object_type, ensure_list


class CondaPackageCheck(object):
    def __init__(self, path):
        super(CondaPackageCheck, self).__init__()
        self.path = path
        self.archive = tarfile.open(self.path)
        self.dist = self.retrieve_package_name(self.path)
        self.name, self.version, self.build = self.dist.rsplit('-', 2)
        self.paths = set(member.path for member in self.archive.getmembers())
        self.index = self.archive.extractfile('info/index.json').read()
        self.info = json.loads(self.index.decode('utf-8'))
        self.files_file = self.archive.extractfile('info/files').read()
        self.win_pkg = bool(self.info['platform'] == 'win')
        self.name_pat = re.compile(r'[a-z0-9_][a-z0-9_\-\.]*$')
        self.hash_pat = re.compile(r'[gh][0-9a-f]{5,}', re.I)
        self.version_pat = re.compile(r'[\w\.]+$')
        self.ver_spec_pat = re.compile(r'[\w\.,=!<>\*]+$')

    @staticmethod
    def retrieve_package_name(path):
        path = os.path.basename(path)
        seq = get_bad_seq(path)
        if seq:
            raise PackageError('Found invalid sequence "{}" in package in info/index.json' .format(seq))

        if path.endswith('.tar.bz2'):
            return path[:-8]
        elif path.endswith('.tar'):
            return path[:-4]
        else:
            raise PackageError('Found package with invalid extension "{}"' .format(os.path.splitext(path)[1]))

    def check_package_name(self):
        package_name = self.info.get('name')
        if package_name is None:
            return Error(self.path, 'C1101', 'Missing package name in info/index.json')

        if package_name != self.name:
            return Error(self.path, 'C1102', 'Found package name in info/index.json "{}" does not match filename "{}"' .format(package_name, self.name))

        if not self.name_pat.match(package_name) or package_name.endswith(('.', '-', '_')):
            return Error(self.path, 'C1103', 'Found invalid package name in info/index.json')

    def check_package_version(self):
        package_version = str(self.info.get('version'))
        if not package_version:
            return Error(self.path, 'C1104', 'Missing package version in info/index.json')
        if not self.version_pat.match(package_version) or get_bad_seq(package_version):
            return Error(self.path, 'C1105', 'Found invalid version number in info/index.json')
        if package_version != self.version:
            return Error(self.path, 'C1106', 'Found package version in info/index.json "{}" does not match filename version "{}"' .format(package_version, self.version))
        if package_version.startswith(('_', '.')) or package_version.endswith(('_', '.')):
            return Error(self.path, 'C1107', "Package version in info/index.json cannot start or end with '_' or '.'")

    def check_build_number(self):
        build_number = self.info.get('build_number')
        if build_number is not None:
            try:
                build_number = int(build_number)
                if build_number < 0:
                    return Error(self.path, 'C1109', 'Build number in info/index.json cannot be a negative integer')

            except ValueError:
                return Error(self.path, 'C1108', 'Build number in info/index.json must be an integer')

    def check_build_string(self):
        build_string = self.info.get('build')
        if not self.version_pat.match(build_string):
            return Error(self.path, 'C1110', 'Found invalid build string "{}" in info/index.json' .format(build_string))
        if build_string != self.build:
            return Error(self.path, 'C1111', 'Found build number in info/index.json "{}" does not match build number "{}" in filename' .format(build_string, self.build))
    
    def check_index_dependencies(self):
        depends = self.info.get('depends')
        if depends is None:
            return Error(self.path, 'C1112', 'Missing "depends" field in info/index.json')

    def check_index_dependencies_specs(self):
        dependencies = ensure_list(self.info.get('depends'))
        if dependencies != [None]:
            for dependency in dependencies:
                dependency_parts = dependency.split()
                if len(dependency_parts) == 0:
                    return Error(self.path, 'C1113', 'Found empty dependencies in info/index.json')
                elif len(dependency_parts) == 2 and not self.ver_spec_pat.match(dependency_parts[1]) or len(dependency_parts) > 3:
                    return Error(self.path, 'C1115', 'Found invalid dependency "{}" in info/index.json' .format(dependency))

    def check_license_family(self):
        license = self.info.get('license_family', self.info.get('license'))
        if license not in LICENSE_FAMILIES:
            return Error(self.path, 'C1114', 'Found invalid license "{}" in info/index.json' .format(license))

    def check_index_encoding(self):
        if not all_ascii(self.index, self.win_pkg):
            return Error(self.path, 'C1115', 'Found non-ascii characters inside info/index.json')

    def check_duplicate_members(self):
        if len(self.archive.getmembers()) != len(self.paths):
            return Error(self.path, 'C1116', 'Found duplicate members inside tar archive')

    def check_members(self):
        for member in self.archive.getmembers():
            if sys.version_info.major == 2:
                unicode_path = member.path.decode('utf-8')
            else:
                unicode_path = member.path.encode('utf-8')

            if not all_ascii(unicode_path):
                return Error(self.path, 'C1117', 'Found archive member names containing non-ascii characters')

    def check_files_file_encoding(self):
        if not all_ascii(self.files_file, self.win_pkg):
            return Error(self.path, 'C1118', 'Found filenames in info/files containing non-ascii characters')

    def check_files_file_for_info(self):
        filenames = [path.strip() for path in self.files_file.decode('utf-8').splitlines()]
        for filename in filenames:
            if filename.startswith('info'):
                return Error(self.path, 'C1119', 'Found filenames in info/files that start with "info"')

    def check_files_file_for_duplicates(self):
        filenames = [path.strip() for path in self.files_file.decode('utf-8').splitlines()]
        if len(filenames) != len(set(filenames)):
            return Error(self.path, 'C1120', 'Found duplicate filenames in info/files')

    def check_files_file_for_validity(self):
        members = [member.path for member in self.archive.getmembers()
                   if not member.isdir() and not member.path.startswith('info')]
        filenames = [path.strip() for path in self.files_file.decode('utf-8').splitlines()
                     if not path.strip().startswith('info')]

        for filename in sorted(set(members).union(set(filenames))):
            if filename not in members:
                return Error(self.path, 'C1121', 'Found filename in info/files missing from tar archive: {}' .format(filename))
            elif filename not in filenames:
                return Error(self.path, 'C1122', 'Found filename in tar archive missing from info/files: {}' .format(filename))

    def check_for_hardlinks(self):
        for member in self.archive.getmembers():
            if member.islnk():
                return Error(self.path, 'C1123', 'Found hardlink {} in tar archive' .format(member.path))

    def check_for_unallowed_files(self):
        unallowed_directories = {'conda-meta', 'conda-bld', 'pkgs', 'pkgs32', 'envs'}

        for filepath in self.paths:
            if filepath in unallowed_directories or filepath.endswith(('.DS_Store', '~')):
                return Error(self.path, 'C1124', 'Found unallowed file in tar archive: {}' .format(filepath))
            
    def check_for_noarch_info(self):
        for filepath in self.paths:
            if 'info/package_metadata.json' in filepath or 'info/link.json' in filepath:
                if self.info['subdir'] != 'noarch' and 'preferred_env' not in self.info:
                    return Error(self.path, 'C1125', 'Found {} however package is not a noarch package' .format(filepath))

    def check_for_bat_and_exe(self):
        bat_files = [filepath for filepath in self.paths if filepath.endswith('.bat')]
        exe_files = [filepath for filepath in self.paths if filepath.endswith('.exe')]

        if len(bat_files) > 0 and len(exe_files) > 0:
            return Error(self.path, 'C1126', 'Found both .bat and .exe files in executable directory')

    def check_prefix_file(self):
        for member in self.archive.getmembers():
            if member.path == 'info/has_prefix':
                prefix_file = self.archive.extractfile(member.path).read()
     
                if not all_ascii(prefix_file, self.win_pkg):
                    return Error(self.path, 'C1127', 'Found non-ascii characters in info/has_prefix')
               
                for line in prefix_file.decode('utf-8').splitlines():
                    line = line.strip()
                    try:
                        placeholder, mode, filename = line.split()
                    except ValueError:
                        placeholder, mode, filename = '/<dummy>/<placeholder>', 'text', line
                    
                    if filename not in self.paths:
                        return Error(self.path, 'C1128', 'Found filename "{}" in info/has_prefix not included in archive' .format(filename))

                    if mode not in ['binary', 'text']:
                        return Error(self.path, 'C1129', 'Found invalid mode "{}" in info/has_prefix' .format(mode))

                    if mode == 'binary':
                        if self.name == 'python':
                            return Error(self.path, 'C1130', 'Binary placeholder found in info/has_prefix not allowed when building Python')
                        elif self.win_pkg:
                            return Error(self.path, 'C1131', 'Binary placeholder found in info/has_prefix not allowed in Windows package')
                        elif len(placeholder) != 255:
                            return Error(self.path, 'C1132', 'Binary placeholder "{}" found in info/has_prefix does not have a length of 255 bytes' .format(placeholder))

    def check_for_post_links(self):
        for filepath in self.paths:
            if filepath.endswith(('-post-link.sh',  '-pre-link.sh',  '-pre-unlink.sh',
                                  '-post-link.bat', '-pre-link.bat', '-pre-unlink.bat')):
                return Error(self.path, 'C1133', 'Found pre/post link file "{}" in archive' .format(filepath))

    def check_for_egg(self):
        for filepath in self.paths:
            if filepath.endswith('.egg'):
                return Error(self.path, 'C1134', 'Found egg file "{}" in archive' .format(filepath))

    def check_for_easy_install_script(self):
        for filepath in self.paths:
            if filepath.startswith(('bin/easy_install', 'Scripts/easy_install')):
                return Error(self.path, 'C1135', 'Found easy_install script "{}" in archive' .format(filepath))

    def check_for_pth_file(self):
        for filepath in self.paths:
            if filepath.endswith('.pth'):
                return Error(self.path, 'C1136', 'Found namespace file "{}" in archive' .format(filepath))

    def check_for_pyo_file(self):
        for filepath in self.paths:
            if filepath.endswith('.pyo') and self.name != 'python':
                return Error(self.path, 'C1137', 'Found pyo file "{}" in archive' .format(filepath))

    def check_for_pyc_in_site_packages(self):
        for filepath in self.paths:
            if filepath.endswith('.pyc') and 'site-packages' not in filepath and 'distutils' not in filepath:
                return Error(self.path, 'C1138', 'Found pyc file "{}" in invalid directory' .format(filepath))

    def check_for_2to3_pickle(self):
        for filepath in self.paths:
            if 'lib2to3' in filepath and filepath.endswith('.pickle'):
                return Error(self.path, 'C1139', 'Found lib2to3 .pickle file "{}"' .format(filepath))

    def check_pyc_files(self):
        if 'py3' not in self.build:
            for filepath in self.paths:
                if '/site-packages/' in filepath:
                    if filepath.endswith('.py') and (filepath + 'c') not in self.paths:
                        return Error(self.path, 'C1140', 'Found python file "{}" without a corresponding pyc file' .format(filepath))

    def check_menu_json_name(self):
        menu_json_files = [filepath for filepath in self.paths
                           if filepath.startswith('Menu/') and filepath.endswith('.json')]

        if len(menu_json_files) == 1:
            filename = menu_json_files[0]
            if filename != '{}.json' .format(self.name):
                return Error(self.path, 'C1141', 'Found invalid Menu json file "{}"' .format(filename))
        elif len(menu_json_files) > 1:
            return Error(self.path, 'C1142', 'Found more than one Menu json file')

    def check_windows_arch(self):
        if self.win_pkg:
            arch = self.info['arch']
            if arch not in ('x86', 'x86_64'):
                return Error(self.path, 'C1143', 'Found unrecognized Windows architecture "{}"' .format(arch))
            
            for member in self.archive.getmembers():
                if member.path.endswith(('.exe', '.dll')):
                    file_header = self.archive.extractfile(member.path).read(4096)
                    file_object_type = get_object_type(file_header)
                    if ((arch == 'x86' and file_object_type != 'DLL I386') or
                        (arch == 'x86_64' and file_object_type != 'DLL AMD64')):
                        
                        return Error(self.path, 'C1144', 'Found file "{}" with object type "{}" but with arch "{}"' .format(member.name, file_object_type, arch))


class CondaRecipeCheck(object):
    def __init__(self, meta, recipe_dir):
        super(CondaRecipeCheck, self).__init__()
        self.meta = meta
        self.recipe_dir = recipe_dir
        self.name_pat = re.compile(r'[a-z0-9_][a-z0-9_\-\.]*$')
        self.version_pat = re.compile(r'[\w\.]+$')
        self.ver_spec_pat = re.compile(r'[\w\.,=!<>\*]+$')
        self.url_pat = re.compile(r'(ftp|http(s)?)://')
        self.hash_pat = {'md5': re.compile(r'[a-f0-9]{32}$'),
                         'sha1': re.compile(r'[a-f0-9]{40}$'),
                         'sha256': re.compile(r'[a-f0-9]{64}$')}

    def check_package_name(self):
        package_name = self.meta.get('package', {}).get('name', '')
        
        if package_name == '':
            return Error(self.recipe_dir, 'C2101', 'Missing package name in meta.yaml')

        if not self.name_pat.match(package_name) or package_name.endswith(('.', '-', '_')):
            return Error(self.recipe_dir, 'C2102', 'Found invalid package name "{}" in meta.yaml' .format(package_name))
        
        seq = get_bad_seq(package_name)
        if seq:
            return Error(self.recipe_dir, 'C2103', 'Found invalid sequence "{}" in package name' .format(seq))

    def check_package_version(self):
        package_version = self.meta.get('package', {}).get('version', '')

        if package_version == '':
            return Error(self.recipe_dir, 'C2104', 'Missing package version in meta.yaml')
        
        if not self.version_pat.match(package_version) or package_version.startswith(('_', '.')) or package_version.endswith(('_', '.')):
            return Error(self.recipe_dir, 'C2105', 'Found invalid package version "{}" in meta.yaml' .format(package_version))
    
        seq = get_bad_seq(package_version)
        if seq:
            return Error(self.recipe_dir, 'C2106', 'Found invalid sequence "{}" in package version' .format(seq))

    def check_build_number(self):
        build_number = self.meta.get('build', {}).get('number')

        if build_number is not None:
            try:
                int(build_number)
            except ValueError:
                return Error(self.recipe_dir, 'C2107', 'Build number in info/index.json must be an integer')

            if build_number < 0:
                return Error(self.recipe_dir, 'C2108', 'Build number in info/index.json cannot be a negative integer')

    def check_fields(self):
        for section in self.meta:
            if section not in FIELDS:
                return Error(self.recipe_dir, 'C2109', 'Found invalid section "{}"' .format(section))

            subfield = self.meta.get(section)
            for key in subfield:
                if key not in FIELDS[section]:
                    return Error(self.recipe_dir, 'C2110', 'Found invalid field "{}" in section "{}"' .format(key, section))
    
    def check_requirements(self):
        build_requirements = self.meta.get('requirements', {}).get('build', [])
        run_requirements = self.meta.get('requirements', {}).get('run', [])
        
        for requirement in build_requirements + run_requirements:
            requirement_parts = requirement.split()
            requirement_name = requirement_parts[0]

            if not self.name_pat.match(requirement_name):
                if requirement in build_requirements:
                    return Error(self.recipe_dir, 'C2111', 'Found invalid build requirement "{}"' .format(requirement))
                elif requirement in run_requirements:
                    return Error(self.recipe_dir, 'C2112', 'Found invalid run requirement "{}"' .format(requirement))
   
            if len(requirement_parts) == 0:
                return Error(self.path, 'C2113', 'Found empty dependencies in info/index.json')
            elif len(requirement_parts) == 2 and not self.ver_spec_pat.match(requirement_parts[1]) or len(requirement_parts) > 3:
                return Error(self.path, 'C2114', 'Found invalid dependency "{}" in info/index.json' .format(requirement))

    def check_about(self):
        summary = self.meta.get('about', {}).get('summary')

        if summary is not None and len(summary) > 80:
            return Error(self.recipe_dir, 'C2115', 'Found summary with length greater than 80 characters')

        home = self.meta.get('about', {}).get('home')
        dev_url = self.meta.get('about', {}).get('dev_url')
        doc_url = self.meta.get('about', {}).get('doc_url')
        license_url = self.meta.get('about', {}).get('license_url')

        for url in [home, dev_url, doc_url, license_url]:
            if url is not None and not self.url_pat.match(url):
                return Error(self.recipe_dir, 'C2116', 'Found invalid URL "{}" in meta.yaml' .format(url))

    def check_source(self):
        source = self.meta.get('source')
        url = source.get('url')
        if url is not None:
            if self.url_pat.match(url):

                for hash_algorithm in ['md5', 'sha1', 'sha256']:
                    hexdigest = source.get(hash_algorithm)
                    if hexdigest is not None and not self.hash_pat[hash_algorithm].match(hexdigest):
                        return Error(self.recipe_dir, 'C2117', 'Found invalid hash "{}" in meta.yaml' .format(hexdigest))

            else:
                return Error(self.recipe_dir, 'C2118', 'Found invalid URL "{}" in meta.yaml' .format(url))
        
        git_url = source.get('git_url')
        if git_url and (source.get('git_tag') and source.get('git_branch')):
            return Error(self.recipe_dir, 'C2119', 'Found both git_branch and git_tag in meta.yaml source field')

    def check_license_family(self):
        license_family = (self.meta.get('about', {}).get('license_family',
                          self.meta.get('about', {}).get('license')))

        if license_family is not None and license_family not in LICENSE_FAMILIES:
            return Error(self.recipe_dir, 'C2120', 'Found invalid license family "{}"' .format(license_family))

    def check_for_valid_files(self):
        test_files = self.meta.get('test', {}).get('files', [])
        test_source_files = self.meta.get('test', {}).get('source_files', [])
        source_patches = self.meta.get('source', {}).get('patches', [])

        for filename in test_files + test_source_files + source_patches:
            filepath = os.path.join(self.recipe_dir, filename)
            if filename.startswith('..'):
                return Error(self.recipe_dir, 'C2121', 'Found file "{}" listed outside recipe directory' .format(filename))

            if not os.path.exists(filepath):
                return Error(self.recipe_dir, 'C2122', 'Found file "{}" in meta.yaml that doesn\'t exist' .format(filename))

    def check_dir_content(self):
        disallowed_extensions = ('.tar', '.tar.gz', '.tar.bz2', '.tar.xz',
                                 '.so', '.dylib', '.la', '.a', '.dll', '.pyd')

        for dirpath, _, filenames in os.walk(self.recipe_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if filepath.endswith(disallowed_extensions):
                    return Error(self.recipe_dir, 'C2123', 'Found disallowed file with extension "{}"' .format(filepath))
