# Linear encodings in DOcplex

CPLEX rejects non-linear terms, so these are the usual linear forms for constructs MIP does
not state directly. Indicators need no big-M: prefer them.

Back to [SKILL.md](../SKILL.md) · API: [`Model`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html)

**How to read the blocks.** Each block is a complete fragment. It assumes this preamble has run,
and defines every variable and constant it uses, so it can be pasted after the preamble:

```python
from docplex.mp.model import Model

m = Model(name="encoding")
```

Each block was run after this preamble, with the enumeration `populate()` compared against a
brute-force enumeration over the same small domains (see [sources.md](../sources.md)).

## All different through an assignment matrix

`pick[i, v] = 1` means position `i` holds value `v`. `x[i]` reads the matrix back as an
expression. Use this instead of pairwise `!=` once there are more than a handful of values.

```python
n, values = 3, range(1, 4)                       # 3 positions, values 1..3
pick = m.binary_var_matrix(range(n), values, name="pick")
for i in range(n):
    m.add_constraint(m.sum(pick[i, v] for v in values) == 1)
for v in values:
    m.add_constraint(m.sum(pick[i, v] for i in range(n)) <= 1)
x = [m.sum(v * pick[i, v] for v in values) for i in range(n)]
```

## Single inequality between two variables

```python
a = m.integer_var(0, 2, name="a")
b = m.integer_var(0, 2, name="b")
m.add_constraint(a != b)   # adds 1 variable and 2 constraints of its own (measured)
```

## Disjunction of linear constraints

At least one of several constraints holds: `a + b <= 2` or `a - b >= 2`. One indicator per
branch, then at least one branch on.

```python
a = m.integer_var(0, 3, name="a")
b = m.integer_var(0, 3, name="b")
branch = m.binary_var_list(2, name="branch")
m.add_indicator(branch[0], a + b <= 2)     # branch 0 active when branch[0] == 1
m.add_indicator(branch[1], 2 <= a - b)
m.add_constraint(m.sum(branch) >= 1)
```

## Absolute value

```python
a = m.integer_var(-2, 2, name="a")
b = m.integer_var(-2, 2, name="b")
d = m.integer_var(0, 4, name="d")          # integer d: abs() alone gives a continuous helper
m.add(d == m.abs(a - b))
```

## Reified equality

`c == 1` exactly when `a == b`:

```python
a = m.integer_var(0, 2, name="a")
b = m.integer_var(0, 2, name="b")
c = m.binary_var(name="c")
m.add_equivalence(c, a == b)
```

`m.add_indicator(c, a == b)` enforces `a == b` only when `c == 1`; it does not force `a != b`
when `c == 0`, so use `add_equivalence` for the full reification.

## Constraint implies constraint

```python
x = m.integer_var(0, 5, name="x")
y = m.integer_var(0, 5, name="y")
m.add_if_then(x >= 3, y == 0)              # if x >= 3 then y == 0
```

## Element: value equals table[index]

```python
table = [5, 1, 4]
index = m.integer_var(0, len(table) - 1, name="index")
value = m.integer_var(0, 9, name="value")
choose = m.binary_var_list(len(table), name="choose")   # one-hot position of index
m.add_constraint(m.sum(choose) == 1)
m.add_constraint(index == m.sum(j * choose[j] for j in range(len(table))))
m.add_constraint(value == m.sum(table[j] * choose[j] for j in range(len(table))))
```

## Counting

`count` is how many of the variables `xs` equal `1`. `pick[i, v]` is the one-hot encoding of
`xs[i]` over the values `0..2`:

```python
xs = m.integer_var_list(3, 0, 2, name="x")
pick = m.binary_var_matrix(range(len(xs)), range(3), name="pick")
for i in range(len(xs)):
    m.add_constraint(m.sum(pick[i, v] for v in range(3)) == 1)
    m.add_constraint(xs[i] == m.sum(v * pick[i, v] for v in range(3)))
count = m.integer_var(0, len(xs), name="count")
m.add_constraint(count == m.sum(pick[i, 1] for i in range(len(xs))))
```

## Product of a binary and an integer

`p == b * a` for `a` in `lo..hi` and `b` binary, with no product term:

```python
lo, hi = 2, 7
a = m.integer_var(lo, hi, name="a")
b = m.binary_var(name="b")
p = m.integer_var(0, hi, name="p")
m.add_constraint(p <= hi * b)
m.add_constraint(p >= lo * b)
m.add_constraint(p <= a - lo * (1 - b))
m.add_constraint(p >= a - hi * (1 - b))
```

Keep `hi` and `lo` as tight as the data allows: a loose big-M weakens the relaxation.

## Integer division and remainder by a constant

`q = a // k` and `r = a % k` for a constant `k > 0` and `a` in `0..hi`:

```python
k, hi = 3, 8
a = m.integer_var(0, hi, name="a")
q = m.integer_var(0, hi // k, name="q")
r = m.integer_var(0, k - 1, name="r")
m.add_constraint(a == k * q + r)
```

## Logical and min/max helpers

```python
a = m.binary_var(name="a")
b = m.binary_var(name="b")
z = m.binary_var(name="z")
o = m.binary_var(name="o")
m.add(z == m.logical_and(a, b))            # binaries only
m.add(o == m.logical_or(a, b))

p = m.integer_var(0, 3, name="p")
q = m.integer_var(0, 3, name="q")
mx = m.integer_var(0, 3, name="mx")
mn = m.integer_var(0, 3, name="mn")
m.add(mx == m.max(p, q))                   # max and min take expressions
m.add(mn == m.min(p, q))
```
