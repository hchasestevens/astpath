"""Functions for searching the XML from file, file contents, or directory."""


from __future__ import print_function
from itertools import islice, repeat
import os
import re
import ast

from astpath.asts import convert_to_xml


class XMLVersions:
    LXML = object()
    XML = object()


try:
    from lxml.etree import tostring
    from lxml import etree
    XML_VERSION = XMLVersions.LXML
except ImportError:
    from xml.etree.ElementTree import tostring
    XML_VERSION = XMLVersions.XML


PYTHON_EXTENSION = '{}py'.format(os.path.extsep)


def _query_factory(verbose=False):
    def lxml_query(element, expression):
        return element.xpath(expression)

    def xml_query(element, expression):
        return element.findall(expression)

    if XML_VERSION is XMLVersions.LXML:
        return lxml_query
    else:
        if verbose:
            print(
                "WARNING: lxml could not be imported, "
                "falling back to native XPath engine."
            )
        return xml_query


def _tostring_factory():
    def xml_tostring(*args, **kwargs):
        kwargs.pop('pretty_print')
        return tostring(*args, **kwargs)

    if XML_VERSION is XMLVersions.LXML:
        return tostring
    else:
        return xml_tostring


if XML_VERSION is XMLVersions.LXML:
    regex_ns = etree.FunctionNamespace('https://github.com/hchasestevens/astpath')
    regex_ns.prefix = 're'

    @regex_ns
    def match(ctx, pattern, strings):
        return any(
            re.match(pattern, s) is not None
            for s in strings
        )

    @regex_ns
    def search(ctx, pattern, strings):
        return any(
            re.search(pattern, s) is not None
            for s in strings
        )


def find_in_ast(xml_ast, expr, query=_query_factory(), node_mappings=None):
    """Find items matching expression expr in an XML AST."""
    results = query(xml_ast, expr)
    return linenos_from_xml(results, query=query, node_mappings=node_mappings)


def linenos_from_xml(elements, query=_query_factory(), node_mappings=None):
    """Given a list of elements, return a list of line numbers."""
    lines = []
    for element in elements:
        try:
            linenos = query(element, './ancestor-or-self::*[@lineno][1]/@lineno')
        except AttributeError:
            raise AttributeError("Element has no ancestor with line number.")
        except SyntaxError:
            # we're not using lxml backend
            if node_mappings is None:
                raise ValueError(
                    "Lines cannot be returned when using native "
                    "backend without `node_mappings` supplied."
                )
            linenos = getattr(node_mappings[element], 'lineno', 0),

        if linenos:
            lines.append(int(linenos[0]))
    return lines


def file_contents_to_xml_ast(contents, omit_docstrings=False, node_mappings=None):
    """Convert Python file contents (as a string) to an XML AST, for use with find_in_ast."""
    parsed_ast = ast.parse(contents)
    return convert_to_xml(
        parsed_ast,
        omit_docstrings=omit_docstrings,
        node_mappings=node_mappings,
    )


def file_to_xml_ast(filename, omit_docstrings=False, node_mappings=None):
    """Convert a file to an XML AST, for use with find_in_ast."""
    with open(filename, 'r') as f:
        contents = f.read()
    return file_contents_to_xml_ast(
        contents,
        omit_docstrings=omit_docstrings,
        node_mappings=node_mappings,
    )


def search(
        directory, expression, print_matches=False, print_xml=False,
        verbose=False, abspaths=False, recurse=True,
        before_context=0, after_context=0, extension=PYTHON_EXTENSION
):
    """
    Perform a recursive search through Python files.

    Only for files in the given directory for items matching the specified
    expression.
    """
    query = _query_factory(verbose=verbose)

    if os.path.isfile(directory):
        if recurse:
            raise ValueError("Cannot recurse when only a single file is specified.")
        files = (('', None, [directory]),)
    elif recurse:
        files = os.walk(directory)
    else:
        files = ((directory, None, [
            item
            for item in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, item))
        ]),)
    global_matches = []
    for root, __, filenames in files:
        python_filenames = (
            os.path.join(root, filename)
            for filename in filenames
            if filename.endswith(extension)
        )
        for filename in python_filenames:
            node_mappings = {}
            try:
                with open(filename, 'r') as f:
                    contents = f.read()
                file_lines = contents.splitlines()
                xml_ast = file_contents_to_xml_ast(
                    contents,
                    node_mappings=node_mappings,
                )
            except Exception:
                if verbose:
                    print("WARNING: Unable to parse or read {}".format(
                        os.path.abspath(filename) if abspaths else filename
                    ))
                continue  # unparseable

            matching_elements = query(xml_ast, expression)

            if print_xml:
                tostring = _tostring_factory()
                for element in matching_elements:
                    print(tostring(xml_ast, pretty_print=True))

            matching_lines = linenos_from_xml(matching_elements, query=query, node_mappings=node_mappings)
            global_matches.extend(zip(repeat(filename), matching_lines))

            if print_matches:
                for match in matching_lines:
                    matching_lines = list(context(
                        file_lines, match - 1, before_context, after_context
                    ))
                    for lineno, line in matching_lines:
                        print('{path}:{lineno:<5d}{sep}\t{line}'.format(
                            path=os.path.abspath(filename) if abspaths else filename,
                            lineno=lineno,
                            sep='>' if lineno == match - 1 else ' ',
                            line=line,
                        ))
                    if before_context or after_context:
                        print()

    return global_matches


def context(lines, index, before=0, after=0, both=0):
    """
    Yield of 2-tuples from lines around the index. Like grep -A, -B, -C.

    before and after are ignored if a value for both is set. Example usage::

        >>>list(context('abcdefghij', 5, before=1, after=2))
        [(4, 'e'), (5, 'f'), (6, 'g'), (7, 'h')]

    :arg iterable lines: Iterable to select from.
    :arg int index: The item of interest.
    :arg int before: Number of lines of context before index.
    :arg int after: Number of lines of context after index.
    :arg int both: Number of lines of context either side of index.
    """
    before, after = (both, both) if both else (before, after)
    start = max(0, index - before)
    end = index + 1 + after
    return islice(enumerate(lines), start, end)
