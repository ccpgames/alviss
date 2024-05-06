import argparse

from alviss import __version__ as version
from alviss import stubber
from alviss.structs.errors import *
import sys


def main():
    parser = argparse.ArgumentParser(description='Generates Python dataclass stubs based on the given alviss type descriptor file.',
                                     epilog=f'Alviss version {version}')

    parser.add_argument('file', help='The Alviss config type descriptor file to generate strubs from.')
    parser.add_argument('-o', '--output', help='File to write the generated stub code to (otherwise its just printed to stdout)',
                        default='', nargs='?')
    parser.add_argument('-f', '--force-overwrite', help='Overwrite existing output file if it exists', action='store_true')
    parser.add_argument('-n', '--class-name',
                        help='The name of the resulting "final" stub class generated when outputting to a file (default is "AlvissConfigStub"). Set to "None" to skip generating the "final" class.',
                        default='AlvissConfigStub')
    parser.add_argument('-x', '--export-all', help='Make all stub class names public and export via __all__ when outputting to a file.',
                        action='store_true')

    loudness_group = parser.add_mutually_exclusive_group()
    loudness_group.add_argument('-s', '--silent', action='store_true',
                                help='Only outputs the resulting rendered code (and errors print to stderr)')
    loudness_group.add_argument('-v', '--verbose', action="store_true",
                                help='Spits out DEBUG level logs')

    args = parser.parse_args()

    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    if not args.silent:
        print(f'Reading and stubbing file: {args.file}...')

    cls_name = 'AlvissConfigStub' if args.class_name is None else args.class_name
    if cls_name.lower().strip() == 'none':
        cls_name = ''

    try:
        if args.output:
            if not args.silent:
                print(f'Writing output to: {args.output}...')

            stubber.SimpleStubMaker().render_stub_classes_to_file(input_file=args.file,
                                                                  output_file=args.output,
                                                                  overwrite_existing=args.force_overwrite,
                                                                  is_private=not args.export_all,
                                                                  class_name=cls_name)
        else:
            if not args.silent:
                print(f'Printing results:')
                print(f'==================================================')

            print(stubber.SimpleStubMaker().render_stub_classes_from_descriptor_file(args.file, class_name=cls_name, is_private=not args.export_all))

            if not args.silent:
                print(f'==================================================')

        if not args.silent:
            print(f'Done!')

    except AlvissError as e:
        if not args.silent:
            print(f'An error occurred: {e!r}')
        else:
            print(f'An error occurred: {e!r}', file=sys.stderr)
        sys.exit(3)


if __name__ == '__main__':
    main()
