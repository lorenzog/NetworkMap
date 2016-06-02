Notes on graph making vs. data source
-------------------------------------

A few blurbs on what each source file can add to the global network graph.

Terminology:

 * "centre node" is the node that collected information in the most recent run

Supported inputs:

 * Arp cache
 * Routing table
 * Traceroute
 * Network adapter information (ifconfig, ipconfig, etc.)

Each input augments the final graph in different ways. Ultimately the tool could present a prioritised list of nodes so that e.g. running a traceroute against the first node will provide the missing information needed to determine the exact number of hops between centre and target, and so on.


### ARP cache

An arp cache would show only direct neighbours (and not all of them). The resulting graph would be a many-to-many dense graph with an unknown centre node, and a set of nodes directly connected to it.

Assumptions:

 * Every node in the cache is a direct neighbour of all other nodes


### Routing table

A routing table shows sources and sinks (borrowing from graph terminlogy), not necessarily directly connected.

Routing entries are:

 * Nodes
 * Networks

Also a routing table could provide the IP of the current node in some form or another. For example in a Windows `route print` command we can see:

          0.0.0.0          0.0.0.0       10.137.2.1      10.137.2.16     10
       10.137.2.0    255.255.255.0         On-link       10.137.2.16    266
      10.137.2.16  255.255.255.255         On-link       10.137.2.16    266
     10.137.2.255  255.255.255.255         On-link       10.137.2.16    266

Where `10.137.2.16` is the address of the ethernet adaptor.

Adding a node from a routing table augments the graph in two ways:

 * If it's in the same network, it's a direct edge
 * If it's in a different network, then:
  * The gateway is a direct edge from the centre node
  * The other network is a new graph to augment, linked to the default gateway by one or more hops


### Traceroute

A traceroute fills in the gaps of a routing table by providing direct edges between hosts. Ideally the tool should suggest which hosts should be tracerouted (first).


### Network Adaptor information

The various `ifconfig`, `ip addr`, `ipconfig` are useful only in linux to know the IP of the centre node.
