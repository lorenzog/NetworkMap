Random notes
============

installing pygraphviz on openbsd requires doing a 'export
CPATH=:/usr/local/include' first.


graph:

    import networkx as nx
    g = nx.Graph()
    g.add_node('foo')
    g.add_node('bar')
    g.add_edge('foo', 'bar')
    nx.nx_agraph.write_dot(g, '/tmp/foo.dot')
    nx.nx_agraph.view_pygraphviz?
    nx.nx_agraph.view_pygraphviz(g)
    import pygraphviz as pgv
    f = pgv.AGraph('/tmp/foo.dot')
    f.layout()
    f.draw('/tmp/foo.png')
    history

