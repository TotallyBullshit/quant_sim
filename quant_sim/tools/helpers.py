
from functools import reduce

def create_lambda(inputs,f):
    temp = 'lambda ' + inputs +':' + f
    return eval(temp)



def toposort2(data):
    """Dependencies are expressed as a dictionary whose keys are items
    and whose values are a set of dependent items. Output is a list of
    sets in topological order. The first set consists of items with no
    dependences, each subsequent set consists of items that depend upon
    items in the preceeding sets.

    >>> print '\\n'.join(repr(sorted(x)) for x in toposort2({
    ...     2: set([11]),
    ...     9: set([11,8]),
    ...     10: set([11,3]),
    ...     11: set([7,5]),
    ...     8: set([7,3]),
    ...     }) )
    [3, 5, 7]
    [8, 11]
    [2, 9, 10]
    http://code.activestate.com/recipes/578272/
    """
    # Ignore self dependencies.
    for k, v in data.items():
        if type(v) != set:
            v = set(v)
    for k, v in data.items():
        v.discard(k)
    # Find all items that don't depend on anything.
    extra_items_in_deps = reduce(set.union, data.itervalues()) - set(data.iterkeys())
    # Add empty dependences where needed
    data.update({item:set() for item in extra_items_in_deps})
    while True:
        ordered = set(item for item, dep in data.iteritems() if not dep)
        if not ordered:
            break
        yield ordered
        data = {item: (dep - ordered)
                for item, dep in data.iteritems()
                    if item not in ordered}
    assert not data, "Cyclic dependencies exist among these items:\n%s" % '\n'.join(repr(x) for x in data.iteritems())


if __name__ == '__main__':
    data = {'winp':set(['up_n','dn_n']),
           'pp':set(['win_p','up_avg','dn_avg']),
           'up_avg':set(['dn_n']),
           'dn_avg':set(['up_n']),
           'ann_roi':set(['roi','yrs'])
           }
    #for item in x for x in toposort2(data):
    d = [item for sublist in toposort2(data) for item in sublist]
    print d
    #print '\n'.join(repr(sorted(x)) for x in toposort2(data))