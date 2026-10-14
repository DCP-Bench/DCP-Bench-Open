# Tested examples

Each block was run in the `pycsp3_ace` image. "Outputs" names the declared outputs; the
harness runs one solve round on instance `{"n": 3}`. Blocks that read `data` are DCP models,
checked with `evaluation.check` (see [dcp-contract.md](dcp-contract.md)).

## Permutation with an intension constraint

Outputs: `x`.

```python
from pycsp3 import *

# the three values must be distinct
x = VarArray(size=3, dom=range(5))
satisfy(
    # the first value plus twice the second is below the third
    x[0] + 2 * x[1] < x[2],
    # the first value is not twice the second
    x[0] != x[1] * 2,
    AllDifferent(x),
)
```

## Tables with a wildcard

Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=3, dom=range(3))
satisfy(
    # the triples must be in the table, where ANY matches any value
    (x[0], x[1], x[2]) in {(0, 1, ANY), (2, ANY, 1)},
)
```

Explicit form, with `Table(scope=..., supports=...)`. Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=3, dom=range(3))
satisfy(
    # the triples must be in the table, where '*' matches any value
    Table(scope=x, supports=[(0, 1, '*'), (2, '*', 1)]),
)
```

Forbidden pairs, with `conflicts`. Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=2, dom=range(2))
satisfy(
    # the pair of zeros is forbidden
    Table(scope=x, conflicts=[(0, 0)]),
)
```

## Counting

Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(3))
satisfy(
    # exactly two cells hold 1
    Count(x, value=1) == 2,
    # at least two distinct values appear
    NValues(x) >= 2,
)
```

Cardinality with per-value ranges, and an Exist. Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=5, dom=range(3))
satisfy(
    # value 0 occurs 1 to 3 times, value 1 exactly twice, value 2 1 to 3 times
    Cardinality(x, occurrences={0: range(1, 4), 1: 2, 2: range(1, 4)}, closed=True),
    # some cell holds 2
    Exist(x, value=2),
)
```

## Element through a variable index

Outputs: `v`, `t`, `idx`.

```python
from pycsp3 import *

t = VarArray(size=3, dom=[10, 20, 30])
idx = Var(dom=range(3))
v = Var(dom=range(40))
satisfy(
    # the value is the table entry at the index
    v == t[idx],
    # the value is at least 15
    v >= 15,
)
```

## Scheduling: Cumulative and NoOverlap

Outputs: `s`.

```python
from pycsp3 import *

s = VarArray(size=3, dom=range(6))
satisfy(
    # three tasks of length 2 and height 1 share a resource of capacity 2
    Cumulative(origins=s, lengths=[2, 2, 2], heights=[1, 1, 1]) <= 2,
    # the first task starts at time 0
    s[0] == 0,
)
```

Two tasks that must not overlap. Outputs: `s`.

```python
from pycsp3 import *

s = VarArray(size=3, dom=range(6))
satisfy(
    # the tasks must not overlap in time
    NoOverlap(origins=s, lengths=[2, 2, 3]),
    # the first task starts at time 0
    s[0] == 0,
)
```

## Circuit and Channel

Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(4))
satisfy(
    # successors form one Hamiltonian cycle
    Circuit(x),
    # no city is its own successor
    [x[i] != i for i in range(4)],
)
```

Outputs: `x`, `y`.

```python
from pycsp3 import *

x = VarArray(size=3, dom=range(3))
y = VarArray(size=3, dom=range(3))
satisfy(
    # x is a permutation
    AllDifferent(x),
    # y is the inverse permutation of x
    Channel(x, y),
    # the inverse maps 0 to 2
    y[0] == 2,
)
```

## Symmetry breaking with LexIncreasing

Outputs: `x`, `y`.

```python
from pycsp3 import *

x = VarArray(size=2, dom=range(2))
y = VarArray(size=2, dom=range(2))
satisfy(
    # the two rows must be in lexicographic order
    LexIncreasing([x, y]),
    # the first row starts with 1
    x[0] == 1,
)
```

## Minimum and Maximum

Outputs: `x`, `lo`, `hi`.

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(10))
lo = Var(dom=range(10))
hi = Var(dom=range(10))
satisfy(
    # the smallest value is lo
    Minimum(x) == lo,
    # the largest value is hi
    Maximum(x) == hi,
    # the spread is at least 5
    hi - lo >= 5,
)
```

## Conditional constraints

Outputs: `x`, `b`.

```python
from pycsp3 import *

x = VarArray(size=3, dom=range(4))
b = Var(dom=range(2))
satisfy(
    # if x0 is large then x1 is zero
    imply(x[0] > 2, x[1] == 0),
    # b is 1 exactly when the sum exceeds 4
    (b == 1) == (Sum(x) > 4),
    # the else branch fixes x0 to 0
    If(x[2] == 1, Then=x[0] == 3, Else=x[0] == 0),
    # b is 1
    b == 1,
)
```

Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=2, dom=range(3))
satisfy(
    # when x0 is 1, x1 must be 2
    If(x[0] == 1, Then=[x[1] == 2]),
    # x0 is 1
    x[0] == 1,
)
```

Connectives over constraints. Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=3, dom=range(3))
satisfy(
    # x0 or x1 is zero
    Or(x[0] == 0, x[1] == 0),
    # exactly one of x0, x2 is 1
    Xor(x[0] == 1, x[2] == 1),
    # a cell holds 2
    Exist(x, value=2),
)
```

## Two-dimensional arrays

A Latin square row and column constraints. Outputs: `grid`.

```python
from pycsp3 import *

n = 3
grid = VarArray(size=[n, n], dom=range(1, n + 1))
satisfy(
    # every row has distinct values
    [AllDifferent(grid[i]) for i in range(n)],
    # every column has distinct values
    [AllDifferent([grid[i][j] for i in range(n)]) for j in range(n)],
    # the top-left cell is 1
    grid[0][0] == 1,
)
```

A column slice with `grid[:, 0]`. Outputs: `grid`.

```python
from pycsp3 import *

grid = VarArray(size=[2, 3], dom=range(3))
satisfy(
    # column 0 holds distinct values
    AllDifferent(grid[:, 0]),
    # every cell is constrained, so ACE reports it
    [grid[i][j] >= 0 for i in range(2) for j in range(3)],
    # the bottom-right cell is 2
    grid[1][2] == 2,
)
```

## Booleans and coefficients

Outputs: `b`.

```python
from pycsp3 import *

b = VarArray(size=5, dom={0, 1})
satisfy(
    # at least three flags are set
    Sum(b) >= 3,
    # the first flag is off
    b[0] == 0,
)
```

Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=3, dom=range(4))
satisfy(
    # the weighted total is at most 7
    Sum(x[0] * 3, x[1] * 2, x[2] * 5) <= 7,
    # the values add up to at least 3
    x[0] + x[1] + x[2] >= 3,
)
```

## Objectives

Minimise a weighted sum with a generator. Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(3))
w = [3, -1, 2, 0]
# neighbours differ
satisfy(x[i] != x[i + 1] for i in range(3))
# only the positive weights count
minimize(Sum(w[i] * x[i] for i in range(4) if w[i] > 0))
```

Maximise a sum over a permutation. Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=3, dom=range(4))
# the values are distinct
satisfy(AllDifferent(x))
# the total is as large as possible
maximize(Sum(x))
```

## Less common globals

Regular with an automaton. Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(2))
# the bit string has an even number of ones
auto = Automaton(start="q0", transitions=[("q0", 0, "q0"), ("q0", 1, "q1"),
                                          ("q1", 1, "q0"), ("q1", 0, "q1")], final="q0")
satisfy(Regular(scope=x, automaton=auto))
```

Bin packing with bin capacities. Outputs: `b`.

```python
from pycsp3 import *

b = VarArray(size=3, dom=range(2))
# bin 0 holds at most 4, bin 1 at most 3
satisfy(BinPacking(b, sizes=[2, 3, 2], limits=[4, 3]))
```

Knapsack as a constraint. Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=3, dom={0, 1})
# the chosen items have profit at least 6
satisfy(Knapsack(x, weights=[2, 3, 4], wlimit=5, profits=[3, 4, 5]) >= 6)
```

Hamming distance. Outputs: `x`, `y`.

```python
from pycsp3 import *

x = VarArray(size=3, dom=range(2))
y = VarArray(size=3, dom=range(2))
# x and y differ in exactly two positions
satisfy(Hamming(x, y) == 2, x[0] == 1)
```

Index of the maximum. Outputs: `x`, `i`.

```python
from pycsp3 import *

x = VarArray(size=3, dom=range(4))
i = Var(dom=range(3))
# the largest entry is at index i, the last entry is 3
satisfy(MaximumArg(x, rank=TypeRank.FIRST) == i, x[2] == 3, x[0] < 3, x[1] < 3)
```

## Grid symmetry with LexIncreasing (transpose)

Outputs: `x`. Breaks the transpose symmetry of a square grid: the row-major reading is not
after the column-major reading. Verified in the image.

```python
from pycsp3 import *

x = VarArray(size=[2, 2], dom=range(3), id="x")
flat = [x[i][j] for i in range(2) for j in range(2)]
trans = [x[j][i] for i in range(2) for j in range(2)]
satisfy(
    # the row-major reading is not after the column-major reading
    LexIncreasing([flat, trans]),
    # four cells sum to 4
    Sum(flat) == 4,
)
```

## A Regular automaton for a line of cells

Outputs: `x`. Five binary cells holding one block of two ones (a nonogram line with a single
run). The automaton reads one cell per step; the final states accept a line that ends after the
block.

```python
from pycsp3 import *

x = VarArray(size=5, dom={0, 1}, id="x")
auto = Automaton(
    start="s",
    transitions=[("s", 0, "s"), ("s", 1, "b1"), ("b1", 1, "b2"), ("b2", 0, "e"), ("e", 0, "e")],
    final=["b2", "e"],
)
satisfy(
    # the cells read as one run of two ones
    Regular(scope=x, automaton=auto),
    # the line holds two ones
    Sum(x) == 2,
)
```

## Channel with a Table on consecutive pairs

Outputs: `x`. `y` is the inverse of the permutation `x`; each consecutive pair of `y` must not be
equal (a Table of conflicts per pair).

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(4), id="x")
y = VarArray(size=4, dom=range(4), id="y")
satisfy(
    # y is the inverse of x
    Channel(x, y),
    # x is a permutation
    AllDifferent(x),
    # neighbouring entries of y differ
    [Table(scope=(y[i], y[(i + 1) % 4]), conflicts=[(v, v) for v in range(4)]) for i in range(4)],
)
```

## Product of four variables split into binary products

Outputs: `x`. Two auxiliary products, then one product of them. Use this instead of
`Product(x) == K` over four variables, where ACE 2.6 can accept invalid tuples. Verified in the
image: the three solutions reported all multiply to 5040.

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(1, 101), id="x")
p = VarArray(size=2, dom=range(1, 10001), id="p")
satisfy(
    # the product of the first two
    p[0] == x[0] * x[1],
    # the product of the last two
    p[1] == x[2] * x[3],
    # the two partial products multiply to 5040
    p[0] * p[1] == 5040,
)
```

## Element through a VarArray index

Outputs: `x`. `y` is a VarArray, so `y[x[0]]` is an element constraint.

```python
from pycsp3 import *

x = VarArray(size=2, dom=range(3), id="x")
y = VarArray(size=3, dom=range(10), id="y")
satisfy(
    # the second value is the entry of y at the first value
    x[1] == y[x[0]],
    # the first entry of y is 1
    y[0] == 1,
)
```

## Boolean indicators instead of NValues

Outputs: `x`. One Boolean per (node, colour) pair. The indicators are linked to `x` by
reification, and the counting constraints are plain sums. In campaign runs this beat
`NValues` over integer colours on Schur-type constraints; that timing is not re-measured here.
Verified in the image (two solutions reported).

```python
from pycsp3 import *

x = VarArray(size=3, dom=range(3), id="x")
ind = VarArray(size=[3, 3], dom={0, 1}, id="ind")
satisfy(
    # each indicator is 1 exactly when the node has that colour
    [(ind[i][c] == 1) == (x[i] == c) for i in range(3) for c in range(3)],
    # every colour is used by at least one node
    [Sum(ind[i][c] for i in range(3)) >= 1 for c in range(3)],
    # at most two nodes take colour 0
    Sum(ind[i][0] for i in range(3)) <= 2,
)
```

## DCP-Bench models

The complete `model.py` for `csplib_054_n_queens` and `knapsack` is in
[dcp-contract.md](dcp-contract.md#complete-models).
