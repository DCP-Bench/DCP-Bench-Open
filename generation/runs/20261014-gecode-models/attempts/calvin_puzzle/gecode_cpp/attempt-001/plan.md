Grid n x n, cells numbered row-major 0..N-1 (N = n*n). Value k (1..N) sits in cell pos[k-1]; g[c] = k-1 when cell c holds value k.

- fill every square with 1..N exactly once -> channel(*this, g, pos, IPL_DOM) [g[c] = k-1 iff pos[k-1] = c, a permutation]; distinct(*this, pos, IPL_DOM) as redundant help
- next number placed vertically or horizontally exactly three squares away (two-square gap) -> extensional(*this, pos[k], pos[k+1], TupleSet of allowed cell pairs with |dr|=3,dc=0 or dr=0,|dc|=3) for each k
- next number placed diagonally exactly two squares away (one-square gap) -> same table, pair with |dr|=2,|dc|=2 (both kinds share one table: the union of the two move sets, so each step is one of the two move types)
- the table is built from the description's move rules, not from any solution; the grid size n is read from the instance
- output x: outg[c] = g[c] + 1 (values 1..N), output as a Matrix with one list per row
- branching: pos in value order (path search, value k+1 after k) with AFC variable choice, smallest cell first; Luby restarts for the satisfaction search
- objective: none (satisfaction)
