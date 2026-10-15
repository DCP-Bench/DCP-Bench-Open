Requirement: a graph given by adjacency lists (1-based, from the instance) -> node i has Boolean x_i = 1 when it is in the set.
Requirement: no two adjacent nodes are both in the set (independent) -> for each edge {i,j}: linear(*this, BoolVarArgs{x_i, x_j}, IRT_LQ, 1) (Boolean linear, at most one of two).
Requirement: the set is maximal, every node outside it has a neighbour inside it -> for each node i: clause(*this, BOT_OR, {x_i} + {x_j : j neighbour of i}, {}, 1) (at least one true, same form as dcp.h's no-good clause).
Requirement: print nodes as a list of booleans -> output("nodes", x) with x a BoolVarArray of length n from the instance.
Branching: branch(*this, x, BOOL_VAR_NONE(), BOOL_VAL_MIN()) over all decision variables (x is the only decision set; no auxiliaries).
Objective: none (satisfaction).
