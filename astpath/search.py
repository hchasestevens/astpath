import os
import ast

from astpath.asts import convert_to_xml


PYTHON_EXTENSION = '{}py'.format(os.path.extsep)


def find_in_ast(xml_ast, expr, return_lines=True):
    """
    Find items matching expression expr in an XML AST. If 
    return_lines is True, return only matching line numbers, 
    otherwise returning XML nodes.
    """
    results = xml_ast.xpath(expr)
    if return_lines:
        lines = []
        for result in results:
            try:
                linenos = result.xpath('./ancestor-or-self::*[@lineno][1]/@lineno')
            except AttributeError:
                lines.append(result)  # result was a literal
                continue
            if linenos:
                lines.append(int(linenos[0]))
        return lines
    return results


def file_contents_to_xml_ast(contents, omit_docstrings=False, node_mappings=None):
    """
    Convert Python file contents (as a string) to an XML AST,
    for use with find_in_ast.
    """
    parsed_ast = ast.parse(contents)
    return convert_to_xml(parsed_ast, omit_docstrings, node_mappings)


def file_to_xml_ast(filename, omit_docstrings=False, node_mappings=None):
    """
    Convert a file to an XML AST, for use with find_in_ast.
    """
    with open(filename, 'r') as f:
        contents = f.read()
    return file_contents_to_xml_ast(contents, omit_docstrings, node_mappings)


def search(directory, expression, print_matches=True, return_lines=True, show_lines=True, verbose=False):
    """
    Perform a recursive search through Python files in the given
    directory for items matching the specified expression.
    """
    global_matches = []
    for root, __, filenames in os.walk(directory):
        python_filenames = (
            os.path.join(root, filename)
            for filename in 
            filenames
            if filename.endswith(PYTHON_EXTENSION)
        )
        for filename in python_filenames:
            try:
                with open(filename, 'r') as f:
                    contents = f.read()
                if show_lines:
                    file_lines = contents.splitlines()
                xml_ast = file_contents_to_xml_ast(contents)
            except Exception:
                if verbose:
                    print "WARNING: Unable to parse or read {}".format(filename)
                continue  # unparseable
                
            file_matches = find_in_ast(
                xml_ast, 
                expression, 
                return_lines=print_matches or return_lines,
            )
                
            for match in file_matches:
                if print_matches:
                    print '{}:{}{}{}'.format(
                        filename,
                        match,  # will be a line number
                        '::\t' if show_lines else '',
                        file_lines[match - 1] if show_lines else '',
                    )
                else:
                    global_matches.append((filename, match))
    if not print_matches:
        return global_matches
