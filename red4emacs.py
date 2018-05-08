#! /usr/bin/env python

import argparse

from redbaron import RedBaron
from toolz.itertoolz import interpose
"""
First goal: add an argument to a method, not stupidly: sort them,
i.e. put "self" first, put "**kwargs" last, put a named parameter
after a simple one.

Be an interface to emacs functions.

"""


def arg_type_no_comma(arg):
    """The given arg is not a comma (used to filter).
    """
    return arg.get('type') != 'comma'


def interpose_commas(args):
    """Interpose commas args in between the given list of args.
    """
    comma = {
        'first_formatting': [],
        'type': 'comma',
        'second_formatting': [{
            'type': 'space',
            'value': ' '
        }]
    }
    res = interpose(comma, args)
    return list(res)


def arg_type(arg):
    """Type of the arg.
    """
    return arg['type']


def list_argument(arg):
    """
    arg: full arg with key 'type'
    - return: bool
    """
    return True if arg.get('type') == 'list_argument' else False


def dict_argument(arg):
    """
    - return: bool
    """
    return True if arg.get('type') == 'dict_argument' else False


def def_argument(arg):
    """
    - return: bool
    """
    return True if arg.get('type') == 'def_argument' else False


def arg_lower(x, y):
    """Comparaison function, to sort arguments.

    x, y: arg dicts

    types:
    - def_argument, comma, dict_argument

    but in def_argument, we can have named arguments. That one has
    another dict for value.
    """
    X_LT = -1
    X_GT = 1

    if def_argument(x):
        if not def_argument(y):
            return X_LT
        else:
            # Both x and y are def_argument
            # 'self' is always the lower arg.
            if x.get('target') and x.get('target').get('value') == 'self':
                return X_LT
            if y.get('target') and y.get('target').get('value') == 'self':
                return X_GT
            if not y.get('value'):
                # just a simple argument
                return X_GT
            else:
                if not x.get('value'):
                    # x is a simple arg, not a kw
                    return X_LT
            # they're both named args
            return X_GT

    if def_argument(y):
        return X_GT

    if list_argument(x):
        return X_LT

    if dict_argument(x):
        return X_GT

    print("Sorting args: we shouldn't get here !")


def reform_input(args, method="foo"):
    """Re-give the def repr.

    - args: a list of dicts, representing redbaron's arguments

    - return: something like "def foo(args):" (without 'pass')
    """
    # https://redbaron.readthedocs.io/en/latest/nodes_reference.html#funcdefnode
    args = interpose_commas(args)
    newdef = "def {}(): pass".format(method)
    red = RedBaron(newdef)
    red[0].arguments = args
    res = red.dumps().strip()
    res = res.strip(" pass")
    return res


def sort_arguments(txt=""):
    """Txt (str): a valid python code of a def with arguments.

    Be careful, txt must be valid python code.

    example:
    : def foo(arg): pass

    - return: str (the def with sorted arguments).
    """

    if not txt:
        txt = "def foo(first, **kwargs, second=foo): pass"
    red = RedBaron(txt)

    fst = red.fst()[0]
    args = fst['arguments']
    args = [arg
            for arg in args
            if arg_type_no_comma(arg)]
    sargs = args
    res = reform_input(sargs, method=fst['name'])
    return res


def replace_argument(txt, pos, new):
    """
    """
    red = RedBaron(txt)
    fst = red.fst()[0]
    args = fst['arguments']
    args = [arg
            for arg in args
            if arg_type_no_comma(arg)]
    args.pop(pos)
    args.insert(pos, new)
    res = reform_input(args, method=fst['name'])
    return res


if __name__ == "__main__":
    import sys
    txt = "def foo(self, key=val, second): pass"  # testing

    # Parsing command line args with the default module (instead of clize, click,...).
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rename",
        action="store_true",
        help="rename an argument. Must set txt, pos and new")
    parser.add_argument(
        "--txt", help="a valid def line, like 'def foo(arg): pass'")
    parser.add_argument("--pos", help="position of arg to change")
    parser.add_argument("--new", help="new arg")

    parser.add_argument(
        "--sort",
        action="store_true",
        help="Sort the arguments by their type. Must have --txt")

    args = parser.parse_args()

    if args.rename:
        args.txt = args.txt or txt

        if args.pos and args.new:
            exit(replace_argument(args.txt, int(args.pos), args.new))

    elif args.sort:
        args.txt = args.txt or txt
        res = sort_arguments(args.txt)
        exit(res)
