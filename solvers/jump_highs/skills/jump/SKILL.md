---
name: jump
description: JuMP, the Julia modelling language for optimisation, with HiGHS as its mixed-integer linear programming solver. Use when writing, debugging or explaining JuMP models, reading JSON instances, reformulating all-different, table, circuit or indicator constraints for HiGHS, linearising products and disjunctions, or enumerating and proving optimal solutions.
license: Apache-2.0
compatibility: Requires Julia (tested with 1.12.7) and the JuMP, HiGHS.jl and JSON packages (tested with JuMP 1.32.0, HiGHS.jl 1.26.0, JSON 1.10.0); all are free and open source, with no licence key or size limit
metadata:
  domain: constraint-programming
  solver: HiGHS
  paradigm: mip
---

# JuMP (Julia, HiGHS)

JuMP is an algebraic modelling language embedded in Julia. You write variables, constraints and an objective as Julia code, attach a solver, and read the results back. HiGHS solves **linear** constraints and objectives over integer and continuous variables. JuMP reformulates a few constraint sets into linear ones; everything else must be linearised by hand.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Reading input](#reading-input)
- [Modelling](#modelling)
- [Solving](#solving)
- [Printing results](#printing-results)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Examples](#examples)
- [Further reading](#further-reading)

## Install

```bash
julia -e 'using Pkg; Pkg.add(["JuMP", "HiGHS", "JSON"])'
julia -e 'using JuMP, HiGHS, JSON; println(pkgversion(JuMP), " ", pkgversion(HiGHS), " ", pkgversion(JSON))'
```

Tested with Julia 1.12.7, JuMP 1.32.0, HiGHS.jl 1.26.0 (HiGHS 1.15.1) and JSON 1.10.0. Details: [JuMP installation](https://jump.dev/JuMP.jl/stable/installation/), [HiGHS.jl](https://github.com/jump-dev/HiGHS.jl), [JSON.jl](https://github.com/JuliaIO/JSON.jl).

The packages are per environment: a bare Julia session has none of them, and `using JSON` then fails with `Package JSON not found in current path`. Inside a project that already has all three (`julia --project=DIR`, or `JULIA_PROJECT=DIR`), the install step is not needed.

## Quick start

```julia
using JuMP, HiGHS

model = Model(HiGHS.Optimizer)
set_silent(model)
@variable(model, x >= 0, Int)
@variable(model, y >= 0, Int)
@constraint(model, 2x + 3y <= 12)
@constraint(model, x + y <= 4)
@objective(model, Max, 3x + 2y)
optimize!(model)
println(termination_status(model), " x=", value(x), " y=", value(y), " obj=", objective_value(model))
```

Prints `OPTIMAL x=4.0 y=0.0 obj=12.0`. `Model(HiGHS.Optimizer)` attaches HiGHS; `Model()` followed by `set_optimizer(model, HiGHS.Optimizer)` does the same.

## Reading input

To read a JSON data file, parse the path given on the command line, with a default so the script also runs without arguments:

```julia
using JSON

inst = JSON.parsefile(get(ARGS, 1, joinpath(@__DIR__, "instance.json")))
weights = Int.(inst["weights"])          # JSON numbers arrive as Int64 or Float64: convert with Int.
capacity = Int(inst["capacity"])
jobs = inst["jobs"]                      # a list of lists stays a Vector of Vectors
```

- A JSON list of lists is a `Vector{Any}` of vectors, so `jobs[j][k]` indexes it directly. A JSON pair `[machine, duration]` is a two-element vector: `jobs[j][k][1]`.
- Use `Int.(...)` or `Float64.(...)` on the parsed lists before doing arithmetic, so the model gets concrete types.
- Lists may be **ragged** (jobs of different lengths). Take each length from its own list, never from the first one: see [Modelling](#modelling).
- Strings in the instance (names, letters) are `String`: convert with `String(...)` and index a `Dict` built from them; keep them out of constraints.

Working example: [json-input](assets/json-input/README.md).

## Modelling

Full list: [JuMP manual](https://jump.dev/JuMP.jl/stable/manual/constraints/) and [API reference](https://jump.dev/JuMP.jl/stable/api/JuMP/).

| Need | JuMP |
|---|---|
| integer, binary, continuous variable | [`@variable(model, x, Int)`, `@variable(model, b, Bin)`, `@variable(model, c >= 0)`](https://jump.dev/JuMP.jl/stable/manual/variables/) |
| variable per loop pass | [anonymous `h = @variable(model, [1:n], Bin)`](https://jump.dev/JuMP.jl/stable/manual/variables/) (a named one is registered once) |
| one vector per job, sized to that job | `start = [@variable(model, [1:len[j]], lower_bound = 0) for j in 1:n_jobs]`, then `start[j][k]` |
| container indexed from 0 | [`@variable(model, d[0:2], Bin)`](https://jump.dev/JuMP.jl/stable/manual/containers/) |
| linear constraint | [`@constraint(model, 2x + 3y <= 12)`](https://jump.dev/JuMP.jl/stable/manual/constraints/) (`<=`, `>=`, `==`) |
| all different over variables | [`@constraint(model, x in MOI.AllDifferent(n))`](https://jump.dev/MathOptInterface.jl/stable/reference/standard_form/) |
| all different over expressions | `@constraint(model, [q[i] + i for i in 1:n] in MOI.AllDifferent(n))`, every variable bounded (see [n-queens](assets/n-queens/README.md)) |
| allowed tuples | [`@constraint(model, [a, b] in MOI.Table(T))`](https://jump.dev/MathOptInterface.jl/stable/reference/standard_form/), `T` a `Float64` matrix with one tuple per row |
| Hamiltonian circuit | [`@constraint(model, next in MOI.Circuit(n))`](https://jump.dev/MathOptInterface.jl/stable/reference/standard_form/), `next[i]` the 1-based successor of `i` |
| number of distinct values | [`@constraint(model, [k; x] in MOI.CountDistinct(length(x) + 1))`](https://jump.dev/MathOptInterface.jl/stable/reference/standard_form/) |
| how many take a value in a set | [`@constraint(model, [k; x] in MOI.CountBelongs(length(x) + 1, Set([2])))`](https://jump.dev/MathOptInterface.jl/stable/reference/standard_form/) |
| at most one nonzero | [`@constraint(model, x in SOS1(weights))`](https://jump.dev/MathOptInterface.jl/stable/reference/standard_form/) |
| if `b` then linear constraint | [`@constraint(model, b --> {x <= 3})`, `@constraint(model, !b --> {x >= 7})`](https://jump.dev/JuMP.jl/stable/manual/constraints/) |
| minimise / maximise | [`@objective(model, Min, expr)`, `Max`](https://jump.dev/JuMP.jl/stable/manual/objective/), linear `expr` |
| sums and reused expressions | `sum(c[i] * x[i] for i in 1:n)`, [`@expression`](https://jump.dev/JuMP.jl/stable/manual/expressions/) |
| digit-weighted number from variables | `sum(10^(L - k) * d[k] for k in 1:L)`: the value of a word of `L` digits, linear because the powers are constants |

The sets above need **finite bounds** on their variables (see [Common issues](#common-issues)). Not available: `MOI.Reified`, a product of two variables in a constraint or the objective, and `!=` (use the linearisations below).

`AllDifferent` over expressions is enforced, not ignored: `[q[i] + i ...] in MOI.AllDifferent(n)` is OPTIMAL when the queens fit (n = 4, 8) and INFEASIBLE for n = 3.

### Linearisations

| Need | Linear form |
|---|---|
| product of binaries `z = a * b` | `z <= a`, `z <= b`, `z >= a + b - 1` |
| binary times bounded integer `z = b * x`, `0 <= x <= U` | `z <= U * b`, `z <= x`, `z >= x - U * (1 - b)`, `z >= 0` |
| `x` takes value `v` | one `Bin` per value, `sum(is) == 1`, `x == sum(v * is[v] for v in values)` |
| `x != y` | `[x, y] in MOI.AllDifferent(2)` (bounded), or binary `s` with `x - y >= 1 - M * s` and `y - x >= 1 - M * (1 - s)` |
| disjunction of linear constraints | one binary per case, an indicator per case, `sum(cases) >= 1` |
| `d = abs(x - y)` | `d >= x - y`, `d >= y - x` is exact only when `d` is minimised; otherwise binary `s` with `d <= x - y + M * s`, `d <= y - x + M * (1 - s)` |
| value picked by an index variable `c[i]` | the per-value binaries of `i`, `sum(c[v] * is[v] for v in values)` |
| "minimise the number of classes" (colouring) | `x[i, c]` binary per item and class, `sum(x[i, c] for c) == 1`, `x[i, c] + x[j, c] <= 1` per conflict, `x[i, c] <= used[c]`, minimise `sum(used)`; see [graph-colouring](assets/graph-colouring/README.md) |

Keep every big-M as small as the variable bounds allow: a loose one slows HiGHS and can make the numerics wobble. The [scheduling example](assets/scheduling/README.md) uses the disjunction pattern.

The colour-class model is symmetric: any permutation of colours is a solution, which slows large instances. Setting `K` to the number of colours of a greedy colouring (an upper bound) instead of the number of nodes keeps the model correct and smaller.

## Solving

Termination statuses: [JuMP solutions manual](https://jump.dev/JuMP.jl/stable/manual/solutions/). HiGHS options: [HiGHS documentation](https://ergo-code.github.io/HiGHS/stable/).

| Status | Meaning |
|---|---|
| `OPTIMAL` | Proven optimal; for a model without objective, a feasible point was found |
| `INFEASIBLE` | Proven that no solution exists; `has_values` is `false` |
| `INFEASIBLE_OR_UNBOUNDED` | HiGHS cannot tell which; typically an unbounded objective, so bound the variables |
| `TIME_LIMIT` | Limit reached. Check `has_values` before reading values: an incumbent may exist |

| Setting | Call |
|---|---|
| silent output | [`set_silent(model)`](https://jump.dev/JuMP.jl/stable/api/JuMP/#set_silent) |
| time limit in seconds | [`set_time_limit_sec(model, 60.0)`](https://jump.dev/JuMP.jl/stable/api/JuMP/#set_time_limit_sec) or `set_attribute(model, "time_limit", 60.0)` |
| relative MIP gap | `set_attribute(model, "mip_rel_gap", 0.0)`: the reported optimum is then exact |
| threads | `set_attribute(model, "threads", 1)` |

Reading results:

- Integer variables come back as `Float64`: use `round(Int, value(x))`.
- Check `has_values(model)` before `value` or `objective_value`; without a solution their values are garbage.
- `raw_status(model)` gives HiGHS's own name, e.g. `kHighsModelStatusInfeasible`.
- With `mip_rel_gap` 0 and status `OPTIMAL`, the objective is a proven optimum; a `TIME_LIMIT` incumbent is not.

Where errors appear:

| Stage | Example | What you see |
|---|---|---|
| macro expansion | `@constraint(model, x != y)` | `LoadError` naming the line; the whole file fails to load |
| adding a constraint | `@constraint(model, a * b >= 1)`, integer tuple matrix in `MOI.Table` | exception: constraint type not supported by the solver |
| optimise with a product objective | `@objective(model, Min, a * b)` | termination status `OTHER_ERROR`, no exception |
| reformulation into MIP | `MOI.AllDifferent` over unbounded integers | `BridgeRequiresFiniteDomainError` |
| loading a script | `using JSON` in a bare environment | `ArgumentError: Package JSON not found in current path` |

## Printing results

Print results with `println`, converting values first:

```julia
take = [round(Int, value(x[i])) for i in 1:n]          # integers, not 1.0
println("take = [", join(take, ", "), "]")             # take = [1, 0, 1]
```

- Convert each value with `round(Int, ...)` before `join`, or the list prints `1.0`.
- Print a message with `termination_status(model)` when there is no solution to show (`INFEASIBLE`, `TIME_LIMIT` without values), instead of reading `value`; `println(stderr, ...)` writes to standard error.
- Build a `Dict` of letter to digit in the order you need before printing: `Dict` iteration order is not stable.

## All solutions

HiGHS returns one solution per solve. To list all solutions, solve, record the values, forbid that assignment with a **no-good cut**, and repeat until the status is `INFEASIBLE`. Cut over the **decision variables** only: two auxiliary assignments (totals, indicators) can give the same decisions, and cutting over the auxiliaries reports duplicates.

| Variables in the cut | Cut forbidding assignment `a` |
|---|---|
| binaries | `sum(v for v with a = 0) + sum(1 - v for v with a = 1) >= 1` |
| bounded integers | per variable a disjunction `v >= a + 1` or `v <= a - 1`, chosen by binaries, with `M = upper - lower + 1`; full code in [all-solutions](assets/all-solutions/README.md) |

Integer variables without both bounds cannot be cut: bound them first.

**All optimal solutions:** solve, take the optimum `best`, add `obj_expr == best`, call `set_objective_sense(model, MOI.FEASIBILITY_SENSE)`, then enumerate as above. See [all-optimal](assets/all-optimal/README.md).

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| `Unsupported operator != cannot be interpreted as a constraint` | JuMP has no `!=` constraint | use a linearisation from [Linearisations](#linearisations) |
| `Constraints of type ScalarQuadraticFunction ... are not supported` | product of two variables | linearise `z = a * b` |
| `BridgeRequiresFiniteDomainError` | a variable in an `AllDifferent`, indicator or other set has no finite bound | add both bounds |
| `An object of name :helper is already registered` | a named variable created in a loop | anonymous `h = @variable(model, [1:n], Bin)` |
| `Constraints of type VectorOfVariables-in-Table{Int64}` | `MOI.Table` with an integer matrix | pass a `Float64` matrix |
| `MethodError` for `MOI.Reified` | not available in JuMP | use an indicator constraint `b --> {...}` |
| `INFEASIBLE_OR_UNBOUNDED` or unexpected `TIME_LIMIT` | unbounded variables, or a loose big-M | bound the variables; shrink each M to the bounds |
| `NoOptimizer()` error on `optimize!` | no solver attached | `Model(HiGHS.Optimizer)` |
| `Package JSON not found in current path` | the environment has no JSON package | `Pkg.add("JSON")`, or run inside the project that has it |
| `x / y` gives `3.5` where integer division was meant | `/` is float division | `div(x, y)` or `x ÷ y` |
| `a[i, j]` fails on nested lists | JSON-style nested lists index as `a[i][j]` | `a[i][j]`, or `permutedims(reduce(hcat, rows))` for a matrix |
| `BoundsError` on a list of jobs or rows of unequal length | `n_ops = length(jobs[1])` assumes every job has the same length | take the length per job: `n_ops(j) = length(jobs[j])`, one vector per job |
| `UndefVarError` (`i` not defined in local scope), preceded by a warning about an assignment in soft scope | in a script file, a top-level `while` or `for` block reassigns a global variable (`i += 1`, `count += 1`); the block makes it a new local | declare every reassigned variable `global` inside the block (`global i += 1`), or put the loop in a function that returns the result |
| `UndefVarError` after a loop | a variable first assigned inside a loop is local to it | build sums with `sum(... for ...)` or `@expression`, or declare the variable before the loop |
| `MethodError` with a `String` in a constraint | strings are not numbers | keep strings out of constraints; index a `Dict` built in the model |
| Index error on a container | Julia arrays are 1-based and column-major | `x[i, :]` is row `i`; loop with `eachindex` |
| The end of the output shows only `[16] _start()` and `in expression starting at ...` | an uncaught error prints the message first and the stack trace after it; the last lines are the bottom of the stack, not the error | read the first line of stderr that starts with `ERROR:` |

## Examples

Each folder in `assets/` is a standalone program with its own README: run it with `julia model.jl`. The JSON example reads `instance.json` in its folder.

| Example | Pattern |
|---|---|
| [satisfy](assets/satisfy/README.md) | `AllDifferent`, linear side conditions, no objective |
| [n-queens](assets/n-queens/README.md) | `AllDifferent` over affine expressions, no auxiliary variables |
| [cryptarithm](assets/cryptarithm/README.md) | letters as digits, `AllDifferent`, digit-weighted linear equation |
| [json-input](assets/json-input/README.md) | reading a JSON instance, converting numbers, printing by hand |
| [all-solutions](assets/all-solutions/README.md) | repeated solves with no-good cuts over bounded integers |
| [all-optimal](assets/all-optimal/README.md) | maximise, pin the optimum, enumerate over binaries |
| [maximise](assets/maximise/README.md) | integer production plan with a `Max` objective |
| [minimise](assets/minimise/README.md) | set cover with binaries and a `Min` objective |
| [graph-colouring](assets/graph-colouring/README.md) | colour classes, minimise the number of classes used |
| [infeasible](assets/infeasible/README.md) | proven infeasibility and the status check |
| [scheduling](assets/scheduling/README.md) | job shop with ragged jobs and disjunctive no-overlap constraints |

## Further reading

- JuMP manual: <https://jump.dev/JuMP.jl/stable/>
- JuMP API reference: <https://jump.dev/JuMP.jl/stable/api/JuMP/>
- MathOptInterface standard sets (the `MOI.*` names above): <https://jump.dev/MathOptInterface.jl/stable/reference/standard_form/>
- HiGHS options: <https://ergo-code.github.io/HiGHS/stable/>
- JSON.jl: <https://github.com/JuliaIO/JSON.jl>
- Julia scoping rules (the top-level loop trap): <https://docs.julialang.org/en/v1/manual/variables-and-scoping/>
