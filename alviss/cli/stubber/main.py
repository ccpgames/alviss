import argparse

from alviss import __version__ as version
from alviss import stubber


def main():
    parser = argparse.ArgumentParser(description='Renders a single static config from an Alviss formatted file and '
                                                 'its extends, includes and other expressions.',
                                     epilog=f'Alviss version {version}')

    parser.add_argument('file', help='The Alviss formatted config file to read, parse and render')
    parser.add_argument('-o', '--output', help='File to write the results to (otherwise its just printed) to stdout',
                        default='', nargs='?')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='Spits out DEBUG level logs')

    args = parser.parse_args()

    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    print(f'Reading and parsing file: {args.file}...')
    results = quickloader.render_load(args.file)

    if args.output:
        print(f'Writing output to: {args.output}...')
        with open(args.output, 'w') as fout:
            fout.write(results)
    else:
        print(f'Printing results:')
        print(f'==================================================')
        print(results)
        print(f'==================================================')
    print(f'Done!')


if __name__ == '__main__':
    main()
