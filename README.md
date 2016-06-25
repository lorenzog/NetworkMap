Post-exploitation network mapping
=================================

The purpose of this tool is to produce a network diagram by collating network information gathered on remote hosts.

Example:

 * Compromise host A
 * Dump the routing table, ARP table
 * Feed the dumps into this tool
 * Pivot on host B
 * Dump tables
 * Feed tables
 * ...rinse, repeat

 * Ultimately, this tool produces a network diagram showing all hosts reachable
   from A and B. Ideally with pretty icons


Installation
------------

To install:

 1. Set up a virtualenv:

        virtualenv venv
        source venv/bin/activate

 2. Install the required libraries:

    pip install -r requirements.txt


Optional requirements:

 * Graphviz (see below for minimal instructions)


Usage
-----

This command draws a simple graph from a windows ARP file dump:

    python networkmap samples/arp/windows_7_arp.txt

You are not limited to one sample:

    # note that with traceroute you need to specify the IP of the host
    python networkmap samples/traceroute/linux_traceroute.txt --ip 1.2.3.4

To run Python's SimpleHTTPServer, use the `-H` switch:

    python networkmap samples/arp/linux_arp.txt --ip 1.2.3.4 -H

Then point your browser to http://localhost:8000

Alternatively, from the command-prompt use:

    python -m SimpleHTTPServer



### Installing GraphViz

If you want to automatically generate graphs (by default: yes) then you'll need
pygraphviz installed. For debian-based systems:

    apt-get install pkg-config libgraphviz-dev graphviz-dev graphviz libgraphviz

For RPM based systems:

    yum install graphviz graphviz-devel


#### Weird errors when installing pygraphviz

##### Undefined symbol: Agundirected

If you get a similar error to this one on a Debian-based system:

 File "/home/user/dev/NetworkMap/venv/local/lib/python2.7/site-packages/pygraphviz/graphviz.py", line 24, in swig_import_helper
     _mod = imp.load_module('_graphviz', fp, pathname, description)
     ImportError: /home/user/dev/NetworkMap/venv/local/lib/python2.7/site-packages/pygraphviz/_graphviz.so: undefined symbol: Agundirected

Then fix it like that:

    pip uninstall graphviz
    pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"

Source: http://stackoverflow.com/questions/32885486/pygraphviz-importerror-undefined-symbol-agundirected

##### redhat-hardened-cc1 missing

If you get this error on a Fedora-based system:

    gcc: error: /usr/lib/rpm/redhat/redhat-hardened-cc1: No such file or directory

You need to install redhat-rpm-config. Source: http://stackoverflow.com/a/34641068/204634


Possible alternatives
---------------------

P2NMAP (it's a book, comes with source code): https://python-forensics.org/p2nmap/

#### Future:

 * Dump into Excel spreadsheet or SQL database?
 * Import into Microsoft Visio? https://support.office.com/en-gb/article/Create-a-detailed-network-diagram-by-using-external-data-in-Visio-Professional-1d43d1a0-e1ac-42bf-ad32-be436411dc08#bm2

Misc notes
----------

To keep in mind:

 * Graphviz can also do clustering? http://www.graphviz.org/Gallery/undirected/gd_1994_2007.html
 * Graphviz and network maps (icons are a bit ugly tho): http://www.graphviz.org/Gallery/undirected/networkmap_twopi.html
 * For manual graphs (meh) - requires probably generating an output properly formatted like XML. Pain to maintain: https://community.spiceworks.com/topic/521280-i-need-software-that-make-my-whole-network-diagram-automatically
 * JSON seems to be a good way to go: https://networkx.readthedocs.io/en/stable/reference/readwrite.json_graph.html combined with d3: https://github.com/d3/d3/wiki/Tutorials to produce something like http://bl.ocks.org/mbostock/4062045
