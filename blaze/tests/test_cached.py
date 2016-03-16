import pytest

from blaze.cached import Cache
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
    return Cache()


def test_cached_compute_symbol(cache):
    assert compute(x, ns, cache) == compute(x, ns)
    assert cache.cache == {x: 10}
    tm.assert_frame_equal(compute(t, ns, cache), compute(t, ns))
    assert cache.cache.keys() == ns.keys()


def test_cached_compute_exprs(cache):
    assert compute(x * 2, ns, cache) == compute(x * 2, ns)
    assert (compute(t.amount.min() + x, ns, cache) ==
            compute(t.amount.min() + x, ns))
    assert cache.cache.keys() == {x * 2, t.amount.min() + x}
