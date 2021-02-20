#!/usr/bin/python

"""
The Command Line Interface using argparse.

For more help use::

    astpath -h

"""

import os
import argparse

from astpath.search import search


parser = argparse.ArgumentParser()
parser.add_argument('-q', '--quiet', help="hide output of matches", action='store_true',)
parser.add_argument('-v', '--verbose', help="increase output verbosity", action='store_true',)
parser.add_argument('-x', '--xml', help="print only the matching XML elements", action='store_true',)
parser.add_argument('-a', '--abspaths', help="show absolute paths", action='store_true',)
parser.add_argument('-R', '--no-recurse', help="ignore subdirectories, searching only files in the specified directory", action='store_true',)
parser.add_argument('-d', '--dir', help="search directory or file", default='.',)
parser.add_argument('-A', '--after-context', help="lines of context to display after matching line", type=int, default=0,)
parser.add_argument('-B', '--before-context', help="lines of context to display after matching line", type=int, default=0,)
parser.add_argument('-C', '--context', help="lines of context to display before and after matching line", type=int, default=0,)
parser.add_argument('expr', help="search expression", nargs='+',)


def main():
    """Entrypoint for CLI."""
    args = parser.parse_args()

    if os.path.isfile(args.dir):
        recurse = False
        if not args.no_recurse and args.verbose:
            print("WARNING: Not recursing, as a single file was passed.")
    else:
        recurse = not args.no_recurse

    before_context = args.before_context or args.context
    after_context = args.after_context or args.context
    if (before_context or after_context) and args.quiet:
        print("ERROR: Context cannot be specified when suppressing output.")
        exit(1)

    search(
        args.dir,
        ' '.join(args.expr),
        print_xml=args.xml,
        print_matches=not args.quiet,
        verbose=args.verbose,
        abspaths=args.abspaths,
        recurse=recurse,
        before_context=before_context,
        after_context=after_context,
    )


if __name__ == "__main__":
    main()
