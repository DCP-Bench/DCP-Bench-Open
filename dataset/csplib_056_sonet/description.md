In the SONET problem, we are given a set of nodes and the traffic demand for each pair of nodes. The nodes are connected
by a set of rings. A node is installed on a ring using an add-drop multiplexer (ADM). For two nodes to communicate,
they must be on at least one common ring. Each ring has a capacity, limiting the number of nodes it can host. The
objective is to satisfy all communication demands while minimizing the total number of ADMs used.

Print the total number of ADMs used (total_adms), and the configuration of nodes on rings (ring_config) where
ring_config[k, i] is 1 if node i is on ring k, 0 otherwise.
