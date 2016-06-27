from os.path import isfile, join
from optparse import OptionParser

from recipe import validate_recipe


def main():
    p = OptionParser()

    p.add_option('-v', "--verbose",
                 action="store_true")

    opts, args = p.parse_args()

    for path in args:
        meta_path = join(path, 'meta.yaml')
        if not isfile(meta_path):
            if opts.verbose:
                print("Ignoring: %s" % path)
            continue
        if opts.verbose:
            print("Validating recipe: %s" % path)
        validate_recipe(path)


if __name__ == '__main__':
    main()
