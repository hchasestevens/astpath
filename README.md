# astpath
[![PyPI version](https://badge.fury.io/py/astpath.svg)](https://badge.fury.io/py/astpath)

[e ɛs ti pæθ] _n_.

Ⅰ. A command-line utility for querying Python ASTs using XPath syntax.

ⅠⅠ. A better way of searching through your codebase.

## Example usage
_Finding all usages of the_ `eval` _builtin:_
```bash
$ astpath ".//Call/func/Name[@id='eval']" | head -5
./rlcompleter.py:136    >            thisobject = eval(expr, self.namespace)
./warnings.py:176       >            cat = eval(category)
./rexec.py:328  >        return eval(code, m.__dict__)
./pdb.py:387    >                    func = eval(arg,
./pdb.py:760    >            return eval(arg, self.curframe.f_globals,
```

_Finding all numbers:_
```bash
$ astpath ".//Num" | head -5
./DocXMLRPCServer.py:31 >        here = 0
./DocXMLRPCServer.py:41 >        while 1:
./DocXMLRPCServer.py:57 >            elif text[end:end+1] == '(':
./DocXMLRPCServer.py:82 >                    args[1:],
./DocXMLRPCServer.py:96 >            argspec = object[0] or argspec
```

_... that are never assigned to a variable:_
```bash
$ astpath ".//Num[not(ancestor::Assign)]" | head -5
./DocXMLRPCServer.py:41 >        while 1:
./DocXMLRPCServer.py:57 >            elif text[end:end+1] == '(':
./DocXMLRPCServer.py:201        >                assert 0, "Could not find method in self.functions and no "\
./DocXMLRPCServer.py:237        >        self.send_response(200)
./DocXMLRPCServer.py:252        >                 logRequests=1, allow_none=False, encoding=None,
```

_... and are greater than 1000:_
```bash
$ astpath ".//Num[not(ancestor::Assign) and number(@n) > 1000]" | head -5
./decimal.py:959      >                    return 314159
./fractions.py:206    >    def limit_denominator(self, max_denominator=1000000):
./pty.py:138  >    return os.read(fd, 1024)
./whichdb.py:94       >    if magic in (0x13579ace, 0x13579acd, 0x13579acf):
./whichdb.py:94       >    if magic in (0x13579ace, 0x13579acd, 0x13579acf):
```

_Finding names longer than 42 characters:_
```bash
$ astpath "//Name[string-length(@id) > 42]"
./site-packages/setuptools/dist.py:59   >_patch_distribution_metadata_write_pkg_info()
./site-packages/setuptools/command/easy_install.py:1759 >        updater=clear_and_remove_cached_zip_archive_directory_data)
./test/test_reprlib.py:268      >        module = areallylongpackageandmodulenametotestreprtruncation
./test/test_argparse.py:2744    >    MEPBase, TestMutuallyExclusiveOptionalsAndPositionalsMixed):
```

_Finding_ `except` _clauses that raise a different exception class than they catch:_
```bash
$ astpath "//ExceptHandler[body//Raise/exc//Name and not(contains(body//Raise/exc//Name/@id, type/Name/@id))]" | head -5
./hashlib.py:144        >except ImportError:
./plistlib.py:89        >        except KeyError:
./plistlib.py:103       >        except KeyError:
./nntplib.py:868        >        except ValueError:
./argparse.py:1116      >        except KeyError:
```

_Finding beginnings of unreachable code blocks:_
```bash
$ astpath "//body/*[preceding-sibling::Return or preceding-sibling::Raise][1]"
./unittest/test/testmock/testhelpers.py:381     >        class Foo(object):
./test/test_deque.py:16 >    yield 1
./test/test_posix.py:728        >            def _create_and_do_getcwd(dirname, current_path_length = 0):
```

_Finding candidates for replacement with_ `sum`_:_
```bash
$ astpath -A 1 "//For/body[AugAssign/op/Add and count(child::*)=1]" | head -6
./functools.py:374      >        for item in sorted_items:
./functools.py:375                   key += item
./statistics.py:177     >    for d, n in sorted(partials.items()):
./statistics.py:178              total += Fraction(n, d)
./pstats.py:512 >    for calls in callers.values():
./pstats.py:513          nc += calls
```

_Finding classes matching a regular expression:_
```bash
$ astpath "//ClassDef[re:match('.*Var', @name)]" | head -5
./typing.py:452  >      class TypeVar(_TypingBase, _root=True):
./typing.py:1366 >      class _ClassVar(_FinalTypingBase, _root=True):
./tkinter/__init__.py:287  >    class Variable:
./tkinter/__init__.py:463  >    class StringVar(Variable):
./tkinter/__init__.py:485  >    class IntVar(Variable):
```

`astpath` can also be imported and used programmatically:
```python
>>> from astpath import search
>>> len(search('.', '//Print', print_matches=False))  # number of print statements in the codebase
751
```

## Installation
It is recommended that `astpath` be installed with the optional `lxml` dependency, to allow full use of the XPath query language. 
To do so,
```
pip install astpath[xpath]
```

Alternatively, a no-dependency version using Python's builtin XPath subset can be installed via
```
pip install astpath
```

`astpath` supports both Python 2.7 and 3.x.

## Links
* [Green tree snakes](https://greentreesnakes.readthedocs.io/en/latest/) - a very readable overview of Python ASTs.
* Official `ast` module documentation for [Python 2.7](https://docs.python.org/2.7/library/ast.html) and [Python 3.X](https://docs.python.org/3/library/ast.html).
* [Python AST Explorer](https://python-ast-explorer.com/) for worked examples of ASTs.
* A [brief guide to XPath](http://www.w3schools.com/xml/xpath_syntax.asp).
* [`bellybutton`](https://github.com/hchasestevens/bellybutton), a fully-featured linting engine built on `astpath`.

## Contacts

* Name: [H. Chase Stevens](http://www.chasestevens.com)
* Twitter: [@hchasestevens](https://twitter.com/hchasestevens)

