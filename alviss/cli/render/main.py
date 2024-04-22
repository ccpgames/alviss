import argparse

from alviss import __version__ as version
from alviss.renderers import SimpleStaticRenderer
from alviss.structs.errors import *

import sys


def main():
    parser = argparse.ArgumentParser(description='Renders a single static config from an Alviss formatted file and '
                                                 'its extends, includes and other expressions.',
                                     epilog=f'Alviss version {version}')

    parser.add_argument('file', help='The Alviss formatted config file to read, parse and render')
    parser.add_argument('-o', '--output', help='File to write the results to (otherwise its just printed to stdout)',
                        default='', nargs='?')
    parser.add_argument('-f', '--force-overwrite', help='Overwrite existing output file if it exists',
                        action='store_true')

    loudness_group = parser.add_mutually_exclusive_group()
    loudness_group.add_argument('-s', '--silent', action='store_true',
                                help='Only outputs the resulting rendered config (and errors print to stderr)')
    loudness_group.add_argument('-v', '--verbose', action="store_true",
                                help='Spits out DEBUG level logs')

    args = parser.parse_args()

    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    if not args.silent:
        print(f'Reading and parsing file: {args.file}...')

    try:
        if args.output:
            if not args.silent:
                print(f'Writing output to: {args.output}...')

            SimpleStaticRenderer().render_static_config_to_file(input_file=args.file,
                                                                output_file=args.output,
                                                                overwrite_existing=args.force_overwrite)

        else:
            if not args.silent:
                print(f'Printing results:')
                print(f'==================================================')
            print(SimpleStaticRenderer().render_static_config_from_file(args.file))

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
