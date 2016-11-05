import os
import ast

from astpath.asts import convert_to_xml


PYTHON_EXTENSION = '{}py'.format(os.path.extsep)


def _query_factory(verbose=False):
    def lxml_query(element, expression):
        return element.xpath(expression)
    
    def xml_query(element, expression):
        return element.findall(expression)
    
    try:
        import lxml
    except ImportError:
        if verbose:
            print (
                "WARNING: lxml could not be imported, "
                "falling back to native XPath engine."
            )
        return xml_query
    else:
        return lxml_query


def find_in_ast(xml_ast, expr, return_lines=True, query=_query_factory(), node_mappings=None):
    """
    Find items matching expression expr in an XML AST. If 
    return_lines is True, return only matching line numbers, 
    otherwise returning XML nodes.
    """
    results = query(xml_ast, expr)
    
    if not return_lines:
        return results
    
    lines = []
    for result in results:
        try:
            linenos = query(
                result,
                './ancestor-or-self::*[@lineno][1]/@lineno'
            )
        except AttributeError:
            raise AttributeError(
                "Element has no ancestor with line number."
            )
        except SyntaxError:
            # we're not using lxml backend
            if node_mappings is None:
                raise ValueError(
                    "Lines cannot be returned when using native"
                    "backend without `node_mappings` supplied."
                )
            linenos = getattr(node_mappings[result], 'lineno', 0),
            
        if linenos:
            lines.append(int(linenos[0]))
    return lines


def file_contents_to_xml_ast(contents, omit_docstrings=False, node_mappings=None):
    """
    Convert Python file contents (as a string) to an XML AST,
    for use with find_in_ast.
    """
    parsed_ast = ast.parse(contents)
    return convert_to_xml(
        parsed_ast, 
        omit_docstrings=omit_docstrings, 
        node_mappings=node_mappings,
    )


def file_to_xml_ast(filename, omit_docstrings=False, node_mappings=None):
    """
    Convert a file to an XML AST, for use with find_in_ast.
    """
    with open(filename, 'r') as f:
        contents = f.read()
    return file_contents_to_xml_ast(
        contents, 
        omit_docstrings=omit_docstrings, 
        node_mappings=node_mappings,
    )


def search(directory, expression, print_matches=True, return_lines=True, show_lines=True, verbose=False, abspaths=False):
    """
    Perform a recursive search through Python files in the given
    directory for items matching the specified expression.
    """
    if show_lines and not return_lines:
        raise ValueError("`return_lines` must be set if showing lines.")
        
    query = _query_factory(verbose=verbose)
    
    global_matches = []
    for root, __, filenames in os.walk(directory):
        python_filenames = (
            os.path.join(root, filename)
            for filename in 
            filenames
            if filename.endswith(PYTHON_EXTENSION)
        )
        for filename in python_filenames:
            node_mappings = {}
            try:
                with open(filename, 'r') as f:
                    contents = f.read()
                if show_lines:
                    file_lines = contents.splitlines()
                xml_ast = file_contents_to_xml_ast(
                    contents, 
                    node_mappings=node_mappings,
                )
            except Exception:
                if verbose:
                    print "WARNING: Unable to parse or read {}".format(
                        os.path.abspath(filename) if abspaths else filename
                    )
                continue  # unparseable
                
            file_matches = find_in_ast(
                xml_ast, 
                expression, 
                return_lines=print_matches or return_lines,
                query=query,
                node_mappings=node_mappings,
            )
                
            for match in file_matches:
                if print_matches:
                    print '{}:{}{}{}'.format(
                        os.path.abspath(filename) if abspaths else filename,
                        match,  # will be a line number
                        '\t>' if show_lines else '',
                        file_lines[match - 1] if show_lines else '',
                    )
                else:
                    global_matches.append((filename, match))
                    
    if not print_matches:
        return global_matches
