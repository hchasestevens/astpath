#!/usr/bin/python
import os
import argparse

from astpath.search import search


parser = argparse.ArgumentParser()
parser.add_argument('--hide-lines', help="hide source lines, showing only line numbers", action='store_true',)
parser.add_argument('--verbose', help="increase output verbosity", action='store_true',)
parser.add_argument('--abspaths', help="show absolute paths", action='store_true',)
parser.add_argument('--no-recurse', help="ignore subdirectories, searching only files in the specified directory", action='store_true',)
parser.add_argument('--dir', help="search directory or file", default='.',)
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
        
    search(
        args.dir, 
        ' '.join(args.expr), 
        show_lines=not args.hide_lines,
        verbose=args.verbose,
        abspaths=args.abspaths,
        recurse=recurse,
    )
    
    
if __name__ == "__main__":
    main()
