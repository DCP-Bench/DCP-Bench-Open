# jump_highs: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how JuMP
(Julia, HiGHS) expresses it. Runner: [run.py](run.py), which starts the Julia driver
[driver.jl](driver.jl) in a separate `julia` process and relays its records through
[runner/runtime.py](../../runner/runtime.py). The driver does the solving.

## Submission file

One Julia file, `model.jl`, included into `Main`. It may use `JuMP`, `HiGHS`, `JSON` and
Julia's standard libraries; no other package is installed, and no other file of yours is
staged.

## Entrypoint

```julia
function build(instance)::Tuple{JuMP.Model, AbstractDict}
```

The driver includes the file and calls `build(instance)` once. It must return a 2-tuple
`(model, outputs)` with `model` a `JuMP.Model`. Write `Model()`: the driver attaches
HiGHS with `set_optimizer`, replacing any optimizer you set. Anything printed goes to
stderr.

## Instance

`instance` is a `Dict{String, Any}` parsed from the JSON: `instance["n"]`. Arrays arrive
as `Vector{Any}`, nested arrays as vectors of vectors, **1-based**: `instance["c"][i][j]`,
not `[i, j]`. Strings are `String`, Booleans `Bool`, objects `Dict`.

## Outputs

`outputs` is a non-empty `AbstractDict` from each declared output name (keys go through
`string`, so `"x"` or `:x`) to a `VariableRef`, an affine expression, an `Integer`, a
`Bool`, or an array/tuple of these. A `Matrix` is written as its list of rows, an
n-dimensional array nested by its first index, and a `DenseAxisArray` (e.g.
`@variable(model, d[0:2])`) as its data in index order. Variable and expression values
are rounded and must be within 1e-5 of an integer. A `Bin` output is reported as `0`/`1`.
A `SparseAxisArray` or a quadratic expression is rejected (`execution_error`).

## Objective

`@objective(model, Min, expr)` or `@objective(model, Max, expr)`, linear. No objective
(`FEASIBILITY_SENSE`) is a satisfaction problem.

## Solving

- Forced by the driver after `build`: `set_optimizer(model, HiGHS.Optimizer)`,
  `set_silent`, `threads = 1`, `mip_rel_gap = 0` (so `OPTIMAL` means proven) and a time
  limit per solve.
- Status: `OPTIMAL` with a feasible point is an answer; `INFEASIBLE` and
  `INFEASIBLE_OR_UNBOUNDED` are `unsat` (no re-solve); `DUAL_INFEASIBLE` is `error`
  (objective unbounded); `TIME_LIMIT` is `timeout`, including a feasible point HiGHS did
  not prove; any other status is `error`.
- Enumeration (only when `solution_limit > 1`) pins the objective within 1e-5 of the
  proven optimum, then adds a big-M no-good per answer over the variables under the
  declared outputs (a binary indicator below and above each current value). A repeated
  output value is re-solved, not emitted. Infeasible after a no-good, or every variable
  fixed, is `complete`.
- Time: `run.py` gives the driver a deadline 2 s inside the budget; each solve gets the
  time left minus 0.5 s, and under 0.5 s left is `timeout`. Package loading, `build` and
  JIT compilation spend the same budget. A driver still running 1 s before the budget
  ends is killed and reported as `timeout`, after relaying the solutions it recorded.

## Compilation

None, but loading the packages and compiling the first solve take part of the execution
budget.

## Environment

Image `dcp-eval/jump_highs:v1`: Julia 1.12.7 (`/usr/local/julia/bin/julia`), JuMP 1.32.0,
HiGHS.jl 1.26.0 (HiGHS_jll 1.15.1), JSON 1.10.0, pinned in [Manifest.toml](Manifest.toml)
and precompiled into the read-only depot `/opt/julia-depot`. `JULIA_PROJECT=/opt/jump`
is the environment that makes `using JuMP, HiGHS, JSON` resolve;
`JULIA_DEPOT_PATH=/tmp/julia-depot:/opt/julia-depot` puts anything Julia writes in `/tmp`,
and `JULIA_PKG_OFFLINE=true`: nothing can be added, and the container has no network.
No licence. The runner itself is Python 3.11.2 (`/usr/bin/python3`), which the submission
never sees. For an ad hoc run, `--entrypoint sh` bypasses `/opt/runner/run.py`; `julia`
then picks up the same project.

## Traps

- With `solution_limit > 1`, every variable under an output (directly or inside an
  expression) must be `Int` or `Bin` with finite lower and upper bounds; otherwise the
  driver reports `unsupported`. The no-good cut is a big-M built from those bounds.
- The no-good is over the variables an output is built from, not its value: an output
  expression over many variables makes the driver re-solve through every assignment
  with the same value. Declare such an output as its own bounded `Int` variable tied by
  an equality.
- The driver relays a `String` output leaf unchanged instead of failing, and the
  evaluator then rejects it as `invalid_output` ("Expected integer").

## Example

The pilot fixture [tests/fixtures/model_jump.jl](../../tests/fixtures/model_jump.jl)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```julia
using JuMP

function build(instance)
    n = instance["n"]
    model = Model()
    @variable(model, 0 <= x <= n, Int)
    @variable(model, 0 <= y <= n, Int)
    if instance["optimize"]
        @constraint(model, x + y >= n)
        @objective(model, Min, x + y)
    else
        @constraint(model, x + y == n)
    end
    return model, Dict("x" => x, "y" => y)
end
```
