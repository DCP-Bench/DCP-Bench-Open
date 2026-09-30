---
name: jump
description: Write instance-agnostic JuMP (Julia) models for the DCP-Bench jump_highs integration, solved by HiGHS as mixed-integer programs. Covers the build(instance) contract, how instance data and outputs are represented, the constraint-programming sets JuMP reformulates into MIP for HiGHS, the linearisations the rest needs, and the bounds enumeration depends on.
---

# JuMP models for `jump_highs`

Write one Julia file that defines `build(instance)` and returns a JuMP model and
its declared outputs. The runner attaches HiGHS, solves, proves the optimum when
there is an objective, enumerates distinct solutions and writes them out. You
never call `optimize!`, `value` or `println` for the answer.

Image: Julia 1.12.7 with JuMP 1.32.0, HiGHS.jl 1.26.0 (HiGHS 1.15.1) and JSON
1.10.0, plus the Julia standard library. No other package is installed and there
is no network.

## The contract

```julia
using JuMP

function build(instance)
    n = instance["n"]
    model = Model()
    @variable(model, 0 <= x <= n, Int)
    @variable(model, 0 <= y <= n, Int)
    @constraint(model, x + y == n)
    return model, Dict("x" => x, "y" => y)
end
```

- **`Model()`, without an optimizer.** The runner calls `set_optimizer` with
  HiGHS itself and sets one thread, silence, the time limit and a relative MIP
  gap of 0, so an optimum it reports is proven. Do not set solver attributes.
- **`instance`** is the instance JSON as a `Dict{String, Any}`: `instance["n"]`.
  - JSON arrays arrive as `Vector{Any}` and nested arrays as vectors of
    vectors, indexed 1-based: `instance["cost"][i][j]`.
    `permutedims(reduce(hcat, rows))` turns a list of rows into a `Matrix`.
  - Strings arrive as `String`, `true`/`false` as `Bool`, objects as `Dict`.
- **The outputs** are a `Dict` from each declared output name, exactly as the
  problem declares it (`"A"`, `"total_cost"`), to a value: a variable, an affine
  expression, an integer, a `Bool`, a string, or an array of these. A `Matrix`
  is written as its list of rows, and a variable container indexed from 0
  (`@variable(model, d[0:2])`) as a list in index order.
- **Outputs are integers.** Every output variable must come back integral; a
  fractional value is an error. A declared Boolean output is a `Bin` variable,
  and 0/1 is accepted for it.
- **For enumeration, output variables must be integer and bounded.** The
  runner finds further solutions by adding no-good cuts over the variables the
  outputs are built from, which needs `Int` or `Bin` variables with finite
  lower and upper bounds. A continuous or unbounded one makes the runner report
  `unsupported`. Auxiliary variables that are not outputs may be anything.
- **Give a total its own variable.** An output that is an expression is cut
  over every variable in it, so a `total_cost` written as a sum over many
  shipments makes the runner step through every assignment of those shipments
  that has the same total before it can stop. Declare such an output as its own
  bounded `Int` variable tied by an equality
  (`@variable(model, 0 <= total_cost <= ub, Int)`,
  `@constraint(model, total_cost == sum(...))`), and the cut moves only that
  variable.

### Optimisation

```julia
@objective(model, Min, sum(cost[i][j] * x[i, j] for i in 1:n, j in 1:m))
```

`Min` or `Max` with a linear expression. The runner solves until HiGHS proves
the optimum, then pins the objective to that value and enumerates. A run that
ends before the proof reports a timeout, never a solution. Do not bound the
objective yourself and never put a known optimum into the model.

## HiGHS solves mixed-integer linear programs

Every constraint and the objective must be linear in the variables. Two things
extend that, both checked in this image:

**Constraint-programming sets, which JuMP reformulates into MIP** when every
variable in them has finite bounds (otherwise the reformulation stops with
`BridgeRequiresFiniteDomainError`):

| Constraint | JuMP |
| --- | --- |
| all different | `@constraint(model, x in MOI.AllDifferent(length(x)))` |
| allowed tuples | `@constraint(model, [a, b] in MOI.Table(tuples))`, `tuples` a `Float64` matrix with one tuple per row (an integer matrix is rejected as unsupported) |
| Hamiltonian circuit | `@constraint(model, next in MOI.Circuit(n))`, `next[i]` the 1-based successor of `i` |
| number of distinct values | `@constraint(model, [k; x] in MOI.CountDistinct(length(x) + 1))` |
| how many take a value in a set | `@constraint(model, [k; x] in MOI.CountBelongs(length(x) + 1, Set([2])))` |
| at most one nonzero | `@constraint(model, x in SOS1(weights))` |

**Indicator constraints** switch a linear constraint by a binary:
`@constraint(model, b --> {x <= 3})` and `@constraint(model, !b --> {x >= 7})`.
They too need the variables bounded.

Not available: `MOI.Reified`, and any product of two variables (`a * b`) in a
constraint or the objective, which HiGHS rejects as an unsupported quadratic
constraint. `@constraint(model, x != y)` is not a JuMP constraint at all.

### Linearisations for the rest

- **Product of binaries** `z = a * b`: `z <= a`, `z <= b`, `z >= a + b - 1`.
- **A binary times a bounded integer** `z = b * x` with `0 <= x <= U`:
  `z <= U * b`, `z <= x`, `z >= x - U * (1 - b)`, `z >= 0`.
- **"x takes value v"**: one `Bin` per value, `sum == 1`, and
  `x == sum(v * is[v] for v in values)`; counts, lookups and tables are then
  sums over those binaries.
- **Two variables differ**: `[x, y] in MOI.AllDifferent(2)`, or a binary `s`
  with `x - y >= 1 - M * s` and `y - x >= 1 - M * (1 - s)`.
- **A disjunction** of linear constraints: one binary per case, an indicator for
  each, and `sum(cases) >= 1`.
- **Absolute value** `d = |x - y|`: `d >= x - y` and `d >= y - x` is exact only
  when `d` is minimised. Otherwise add a binary `s` with
  `d <= x - y + M * s` and `d <= y - x + M * (1 - s)`.
- **A value picked by a decision variable** (`c[i]` with `i` a variable): the
  per-value binaries of `i` and `sum(c[v] * is[v] for v in values)`.

Keep every big-M as small as the variables' bounds allow; a loose one slows
HiGHS down and can make the numerics wobble.

## Traps

1. **Bounds on everything that is counted, cut or bridged.** An `Int` variable
   without both bounds breaks enumeration and the constraint-programming sets.
   Derive the bounds from the instance.
2. **Julia is 1-based and column-major.** `x[i, :]` is row `i`; a nested JSON
   list is indexed `a[i][j]`, not `a[i, j]`, until it is made a `Matrix`.
3. **Integer arithmetic on data.** `div(a, b)` or `a ÷ b` for integer division;
   `/` gives a float. `^` is power.
4. **Loops and scope.** Inside `build`, a `for` loop updates a variable that
   exists before it, but a variable first assigned inside the loop does not
   exist after it. Build sums with `sum(... for ...)` or `@expression`.
5. **A named variable is registered once.** `@variable(model, helper, Bin)`
   inside a loop fails on the second pass with ``An object of name `:helper` is
   already registered``; use the anonymous form, `h = @variable(model, [1:n], Bin)`
   or `h = @variable(model, binary = true)`, for per-iteration helpers.
6. **Strings are for output only.** A string instance field can index a `Dict`
   built in the model, but nothing string-valued goes into a constraint.

## What the runner reports

- A syntax or macro error comes back as an error naming the line, for example
  `LoadError: At /input/model.jl:7: @constraint(model, x != y): Unsupported
  operator != cannot be interpreted as a constraint.`
- An infeasible model is `unsat`, and the evaluator reports `no_solution`.
- Loading the packages and the first solve take about 5 to 10 seconds of the
  budget, mostly compilation; later solves in the same run are fast.

## Reasoning to record

Say where each variable's bounds come from in the instance, which
linearisations you used and why the big-M values are what they are.
