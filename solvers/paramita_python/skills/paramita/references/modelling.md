# Paramita modelling: encodings and advice

Paramita has no integer variables. Each integer is a set of Booleans and a linear
expression over them, and the choice of encoding decides whether the solver finishes.
The API calls are in [api.md](api.md); the expression forms are in
[SKILL.md](../SKILL.md#modelling).

## Integers in Booleans

Pick one encoding per integer. Each gives an integer expression usable in PB constraints,
objectives and outputs.

- **One-hot (direct)**, for values that are indexed, matched or all-different:
  `xv = {v: Bool(f"x_{v}") for v in dom}`, `sum(xv.values()) == 1`, value
  `x = sum(v * xv[v] for v in dom)`. "x = 3" is `xv[3]`; "x ≠ y" is `~(xv[v] & yv[v])` per v.
- **Unary (order)**, for values that are summed, bounded or compared. `x > y` over one-hot
  values timed out where unary solved in seconds: `xs = [Bool(f"x_ge_{i}") for i in 1..ub]`,
  `If(xs[i+1], xs[i])`, value `x = sum(xs) + lb`. "x ≥ k" is the single literal `xs[k-1]`.
- **Binary**, for wide ranges (hundreds of values or more, e.g. times): `x = sum(2**k * bit[k])`.
  Unary or one-hot over hundreds of values with pairwise PB constraints ran out of memory.
  Also for the digits of multi-digit numbers in arithmetic (`n = sum(10**k * digit_k)`):
  one-hot digits timed out where binary digits solved in seconds.

## Global-style constraints as PB constraints

| Requirement | Encoding |
|---|---|
| all different | per value v: `sum(xv[v] for x in X) <= 1` (`== 1` for a permutation) |
| value v occurs c times | `sum(xv[v] for x in X) == c` |
| element: y = t[x] | `y = sum(t[v] * xv[v] for v in dom)` (t constant) |
| x + y = k, x ≤ y | PB over the integer expressions: `x + y == k`, `x <= y` |
| table of allowed tuples | one Bool per tuple, `sum(tuple_bools) == 1`, `If(tb, xv[a] & yv[b])` |
| at most u in every window of q | `sum(bs[i:i+q]) <= u` per i |
| no overlap of intervals | one-hot start times; for each time t, `sum(covers_t) <= 1` (see [scheduling](../assets/scheduling/README.md)) |
| product x·y | one Bool per pair `p[a][b] = xv[a] & yv[b]`; avoid when domains are wide |

## Precedence and makespan

Scheduling with durations uses unary start times: `s_ge[j][t]` means "start of task j is at
least t", for t in 1..H (H is a horizon at least the sum of durations). The start is
`sum(s_ge[j])`. Then:

- monotone chain: `If(s_ge[j][t+1], s_ge[j][t])` for each t;
- horizon: `~s_ge[j][t]` for each t above `H - dur_j`;
- end at least t, i.e. start at least `t - dur_j`: when `t - dur_j <= 0` the end is always
  at least t, so the fact is the unit `m_ge[t]` (or `s_ge[b][t]` below), not an `If`;
  when `t - dur_j > H` the end is never at least t, so no clause;
- makespan: `If(end_ge_j[t], m_ge[t])` per task and t, with `m_ge` a monotone unary chain;
  minimise with the objective `-sum(m_ge)` (see Objectives), and the makespan is
  `-(constant + benefit)`;
- precedence a before b: for each t, `If(end_ge_a[t], s_ge[b][t])` (end of a at least t implies
  start of b at least t); when the end of a is always at least t, the unit `s_ge[b][t]`.

```python
for a_, b_ in prec:                       # a finishes before b starts
    for t in range(1, H + 1):
        ea = end_ge(a_, t)                # "TRUE", None (never), or a Bool
        if ea == "TRUE":
            cons.append(s[b_][t])
        elif ea is not None:
            cons.append(If(ea, s[b_][t]))
```

Checked with paramita 1.2.0 on a chain a(2) → b(3) → c(1): makespan 6. Add a no-overlap
constraint (the table above) when tasks share a machine.

## Modelling advice

- Prefer one-hot for anything that is distinct, indexed or matched; unary for quantities
  that are summed. Link two encodings of the same integer with `Iff` per value only when
  both are needed.
- Exactly-one per variable plus at-most-one per value gives the SAT solver strong unit
  propagation; add the redundant "each value used once" for permutations.
- Symmetry: for interchangeable objects, order them (`x_i ≤ x_{i+1}` on the integer
  expressions) or fix the first one.
- Separations between unary integers (`x_i + s ≤ x_j`, e.g. non-overlap of placed squares)
  as clauses, `If(x_j_ge[k], x_i_ge[k+s])` per k, not one PB constraint each: many PB
  separations ran out of memory.
- Objectives: a weighted sum of Bools directly; for "minimise the maximum", introduce unary
  `m` and require `If(load_k_ge_t, m_ge_t)` per t. An objective over a wide range (hundreds
  of values) is best binary: unary there ran out of memory or made the enumeration of
  further optima slow.
- **Shrink objective weights before solving.** EvalMaxSAT proves optima much faster with
  small weights, many of them 0. Where a constraint fixes how many choices are made (each
  demand met exactly, one successor per city), subtract the cheapest cost of each such
  group from all its costs and add the constant back (for a distance matrix: row minima,
  then column minima). This took transport, facility and tour optima from timeouts to
  seconds. A redundant bound such as "open capacity covers total demand" helps the proof
  as well.
- **Keep PB weights small.** A PB constraint with large, distinct weights over many Bools
  (one-hot value × price, a product of two binaries, weights up to 10^4 and beyond) can
  exhaust a 2 GB memory limit. Instead:
  - products and squares: binary bits for the result, linked with
    `If(xv[v], bit_k == ((v*v) >> k) & 1)`, or a column-by-column multiplier;
  - choosing among many constants: `If(choice_q, x == q)` per q with x binary;
  - |a − b| between one-hot positions: a unary length t with `a - b <= t` and `b - a <= t`,
    not one implication per pair of positions;
  - "amount a is payable" for many amounts: a clause-level reachability table
    `r[j][v] ⇔ OR_k (r[j-1][v - k·d_j] ∧ x_j ≥ k)`, not one weighted PB per amount.
- **Wide sums.** The default PB encoder recurses once per term: a single sum of about 5000
  Bools segfaults on an 8 MB stack (2000 did not). Use `ulimit -s unlimited` before the
  interpreter, or split the sum into groups with auxiliary Booleans.
- **Redundant cardinality helps.** A bound that follows from the data (total demand covered,
  each item used at most once) is cheap and shortens both the SAT search and the MaxSAT
  proof.
- **Check the model on small sizes first.** Enumerate all solutions of a small instance and
  compare them with a brute-force count; a wrong encoding usually shows as a count mismatch.

## Reading values back

- The model is a list of signed literals, one per variable up to `solver.max_var()`:
  `true = {abs(l) for l in model if l > 0}`, then `pool.get_variable(b) in true`.
- An integer value is `sum(w * bit)` over the Booleans that are true. For values beyond 32
  bits, read the bits and compute the number in Python integers: the solver's own
  evaluation is 32-bit.
- For a one-hot integer, the value is the index whose Boolean is true; for unary, the number
  of true Booleans plus the lower bound.
