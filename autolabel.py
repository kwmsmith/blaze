import toolz as tz
import toolz.itertoolz as itz
import blaze as bz
from datashape import discover

def valid_name(name):
    return not name.startswith('_')

def stmts_with_subs(terms_and_labels, stmts):
    if not terms_and_labels:
        return stmts
    term, label = itz.first(terms_and_labels)
    sym = bz.symbol(label, dshape=discover(term))
    replaced = [(t._subs({term: sym}), l)
                for (t, l) in itz.rest(terms_and_labels)]
    return stmts_with_subs(replaced, stmts + ((label, term),))


def autolabel(expr, ns):
    ns = {k: v for (k, v) in ns.items()
          if isinstance(v, bz.Expr)}
    names_from_exprs = {}
    for name, exp in ns.items():
        if valid_name(name):
            names_from_exprs.setdefault(exp, set()).add(name)
    subterms = {e for e in expr._subterms()
                if isinstance(e, bz.Expr)}
    label_set = set.intersection(subterms, names_from_exprs)
    contains_graph = {e: {x for x in label_set
                          if e in x and e is not x}
                      for e in label_set}
    ordered_terms = ordered_subterms(contains_graph, ())[::-1]
    labels_and_names = tuple(zip(ordered_terms,
                                 [itz.first(names_from_exprs[e])
                                  for e in ordered_terms]))
    return stmts_with_subs(labels_and_names, ())
    
    # new_expr = expr
    # for exp in ordered_terms:
        # # TODO: detect case when exp is already a `label`ed term.
        # labeled_exp = bz.label(exp, tz.first(names_from_exprs[exp]))
        # new_expr = new_expr._subs({exp: labeled_exp})
    # return new_expr

def statementify(expr, ns):
    return "\n\n".join(["{} = {}".format(label, expr) for (label, expr) in autolabel(expr, ns)])



def remove_ancestor(ancestors, a):
    return {x for x in ancestors if not a.isidentical(x)}


def ordered_subterms(children_graph, ordered_exprs):
    if not children_graph:
        return ordered_exprs
    for descendant, ancestors in children_graph.items():
        if not ancestors:
            parentless = descendant
    new_children_graph = {d: remove_ancestor(a, parentless)
                          for (d, a) in children_graph.items()
                          if not d.isidentical(parentless)}
    return ordered_subterms(new_children_graph,
                            ordered_exprs + (parentless,))
