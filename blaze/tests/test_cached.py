import pytest

from blaze.cached import Cache, CacheyCache
from blaze import symbol, discover, compute, into
import pandas as pd
import pandas.util.testing as tm
from collections import Iterator


df = pd.DataFrame([['Alice', 100, 1],
                   ['Bob', 200, 2],
                   ['Alice', 50, 3]],
                  columns=['name', 'amount', 'id'])

t = symbol('t', discover(df))
x = symbol('x', 'int')
ns = {t: df, x: 10}

@pytest.fixture
def cache():
    return CacheyCache(2*10**9)


def test_cached_compute_symbol(cache):
    assert compute(x, ns, cache) == compute(x, ns)
    assert {k[0] for k in cache.keys()} == {x}
    tm.assert_frame_equal(compute(t, ns, cache), compute(t, ns))
    assert {k[0] for k in cache.keys()} == ns.keys()


def test_cached_compute_exprs(cache):
    assert compute(x * 2, ns, cache) == compute(x * 2, ns)
    assert (compute(t.amount.min() + x, ns, cache) ==
            compute(t.amount.min() + x, ns))
    assert {k[0] for k in cache.keys()} == {x * 2, t.amount.min() + x}


def test_cached_subterms(cache):
    tm.assert_frame_equal(compute(t, ns, cache), compute(t, ns))
    tm.assert_series_equal(compute(t.amount, ns, cache), compute(t.amount, ns))
    assert compute(t.amount.min(), ns, cache) == compute(t.amount.min(), ns)


def test_cached_same_expr_different_data(cache):
    ns0 = {t: df.iloc[:-1], x: 15}
    ns1 = {t: df.iloc[::2], x: -20}
    tm.assert_frame_equal(compute(t, ns0, cache), compute(t, ns0))
    tm.assert_frame_equal(compute(t, ns1, cache), compute(t, ns1))
    tm.assert_series_equal(compute(t.amount, ns0, cache), compute(t.amount, ns0))
    tm.assert_series_equal(compute(t.amount, ns1, cache), compute(t.amount, ns1))
    assert compute(t.amount.min(), ns0, cache) == compute(t.amount.min(), ns0)
    assert compute(t.amount.min(), ns1, cache) == compute(t.amount.min(), ns1)


def test_tiny_cache():
    cache = CacheyCache(1)
    # Yep, that's a cache that can hold one byte of data. IOW, a non-cache :)
    tm.assert_frame_equal(compute(t, ns, cache), compute(t, ns))
    tm.assert_series_equal(compute(t.amount, ns, cache), compute(t.amount, ns))
    assert compute(t.amount.min(), ns, cache) == compute(t.amount.min(), ns)
