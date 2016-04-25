import datashape
import pytest
from datashape import dshape

from blaze import symbol
import blaze as bz

dshapes = ['var * {name: string}',
           'var * {name: ?string}',
           'var * string',
           'var * ?string',
           'string']

@pytest.mark.parametrize('ds', dshapes)
def test_like(ds):
    t = symbol('t', ds)
    expr = getattr(t, 'name', t).str.like('Alice*')
    assert expr.pattern == 'Alice*'
    assert expr.schema.measure == dshape(
        '%sbool' % ('?' if '?' in ds else '')
    ).measure


@pytest.mark.parametrize('ds', dshapes)
def test_str_upper_schema(ds):
    t = symbol('t', ds)
    expr_upper = getattr(t, 'name', t).str.upper()
    expr_lower = getattr(t, 'name', t).str.upper()
    assert (expr_upper.schema.measure ==
            expr_lower.schema.measure ==
            dshape('%sstring' % ('?' if '?' in ds else '')).measure)


def test_str_namespace():
    t = symbol('t', 'var * {name: string}')
    expr_upper_method = t.name.str.upper()
    expr_lower_method = t.name.str.lower()
    expr_upper_lower_methods = t.name.str.upper().str.lower()
    expr_len_method = t.name.str.len()
    expr_like_method = t.name.str.like('*a')

    # expr_upper_func = bz.str.upper(t.name)
    # expr_lower_func = bz.str.lower(t.name)
    # expr_upper_lower_funcs = bz.str.lower(bz.str.upper(t.name))
    # expr_len_func = bz.str.len(t.name)
    # expr_like_func = bz.str.like(t.name, '*a')
