# Plan: csplib_053_graceful_graphs (Gecode, attempt-001)

Requirement: each node gets a unique label from {0, ..., q}, q = number of edges.
  -> distinct(*this, nodes, IPL_DOM) over nodes with domain 0..q

Requirement: an edge xy is labelled |f(x) - f(y)|.
  -> rel(*this, edges[k] == abs(nodes[x] - nodes[y]), default level) for each edge k of the instance graph (domain of edges[k] is 1..q)

Requirement: all edge labels are different.
  -> distinct(*this, edges, IPL_DOM)

Branching: nodes first (first-fail, min value), then the edge labels (propagation fixes most of them).
Objective: none (satisfaction).
