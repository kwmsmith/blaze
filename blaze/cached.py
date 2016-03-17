from __future__ import print_function, division, absolute_import

import time

import numpy as np
import pandas as pd

from datashape import dshape, integral, floating, boolean, complexes
from datashape.predicates import isscalar, isrecord, iscollection

from .interactive import data
from .dispatch import dispatch
from .expr import Expr, ndim, symbol
from .compute import compute
from .compatibility import unicode

from cachey import Cache as CCache

class Cache(object):

    def __init__(self, cache=None):
        self.cache = cache if cache is not None else {}

    def __contains__(self, key):
        return key in self.cache

    def keys(self):
        return self.cache.keys()

    def get(self, key, default=None):
        return self.cache.get(key, default)

    def put(self, key, value, *args, **kwargs):
        self.cache[key] = value

    def clear(self):
        self.cache.clear()


class CacheyCache(Cache):

    def __init__(self, numbytes=10**9):
        self.cache = CCache(numbytes)

    def keys(self):
        return self.cache.data.keys()

    def put(self, key, value, *args, **kwargs):
        self.cache.put(key, value, *args, **kwargs)


def _name_gen():
    i = 0
    while True:
        yield "__%d__" % i
        i += 1
_namer = _name_gen()

def cache_key(expr, scope):
    return (expr, tuple(id(scope[l]) for l in expr._leaves()))


def subs_all(expr, scope, d):
    keys = [cache_key(e, scope) for e in expr._subterms()]
    common_subs = filter(d.__contains__, keys)
    new_scope = scope.copy()
    new_expr = expr
    for key in common_subs:
        sub, _ = key
        new_name = next(_namer)
        while new_name in new_scope:
            new_name = next(_namer)
        new_sym = symbol(new_name, sub.dshape)
        new_expr = new_expr._subs({sub: new_sym})
        new_scope.update({new_sym: d.get(key)})
    return new_expr, new_scope


@dispatch(Expr, dict, CacheyCache)
def compute(expr, d, c, **kwargs):
    key = cache_key(expr, d)
    res = c.get(key)
    if res is not None:
        return res
    new_expr, new_scope = subs_all(expr, d, c)
    return_type = kwargs.pop('return_type', 'core')
    start = time.time()
    result = compute(new_expr, new_scope, return_type=return_type, **kwargs)
    delta = time.time() - start
    c.put(key, result, cost=delta)
    return result


@dispatch(Expr, dict, Cache)
def compute(expr, d, cd, **kwargs):
    res = cd.cache.get(expr)
    if res is not None:
        return res
    return_type = kwargs.pop('return_type', 'core')
    result = compute(expr, d, return_type=return_type, **kwargs)
    cd.put(expr, result)
    return result


@dispatch(Expr, Cache)
def compute(expr, cd, **kwargs):
    resources = expr._resources()
    return compute(expr, resources, cd, **kwargs)
