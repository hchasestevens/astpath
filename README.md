# astpath
[e ɛs ti pæθ] _n_.

Ⅰ. A command-line utility for querying Python ASTs using XPath syntax.

ⅠⅠ. A better way of searching through your codebase.

## Example usage

Finding all usages of the "eval" builtin:
```bash
$ astpath ".//Call/func/Name[@id='eval']" | head -5
./rlcompleter.py:136    >            thisobject = eval(expr, self.namespace)
./warnings.py:176       >            cat = eval(category)
./rexec.py:328  >        return eval(code, m.__dict__)
./pdb.py:387    >                    func = eval(arg,
./pdb.py:760    >            return eval(arg, self.curframe.f_globals,
```

Finding all numbers:
```bash
$ astpath .//Num | head -5
./DocXMLRPCServer.py:31 >        here = 0
./DocXMLRPCServer.py:41 >        while 1:
./DocXMLRPCServer.py:57 >            elif text[end:end+1] == '(':
./DocXMLRPCServer.py:82 >                    args[1:],
./DocXMLRPCServer.py:96 >            argspec = object[0] or argspec
```

... that are never assigned to a variable:
```bash
$ astpath ".//Num[not(ancestor::Assign)]" | head -5
./DocXMLRPCServer.py:41 >        while 1:
./DocXMLRPCServer.py:57 >            elif text[end:end+1] == '(':
./DocXMLRPCServer.py:201        >                assert 0, "Could not find method in self.functions and no "\
./DocXMLRPCServer.py:237        >        self.send_response(200)
./DocXMLRPCServer.py:252        >                 logRequests=1, allow_none=False, encoding=None,
```

... and are greater than 1000:
```bash
$ astpath ".//Num[not(ancestor::Assign) and number(@n) > 1000]" | head -5
./python2.7/decimal.py:959      >                    return 314159
./python2.7/fractions.py:206    >    def limit_denominator(self, max_denominator=1000000):
./python2.7/pty.py:138  >    return os.read(fd, 1024)
./python2.7/whichdb.py:94       >    if magic in (0x13579ace, 0x13579acd, 0x13579acf):
./python2.7/whichdb.py:94       >    if magic in (0x13579ace, 0x13579acd, 0x13579acf):
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

`astpath` supports both Python 2.x and 3.x.

## Links
* [Green tree snakes](https://greentreesnakes.readthedocs.io/en/latest/) - a very readable overview of Python ASTs.
* Official `ast` module documentation for [Python 2.7](https://docs.python.org/2.7/library/ast.html) and [Python 3.X](https://docs.python.org/3/library/ast.html).
* [Python AST Explorer](https://python-ast-explorer.com/) for worked examples of ASTs.
* A [brief guide to XPath](http://www.w3schools.com/xml/xpath_syntax.asp).

## Contacts

* Name: [H. Chase Stevens](http://www.chasestevens.com)
* Twitter: [@hchasestevens](https://twitter.com/hchasestevens)

