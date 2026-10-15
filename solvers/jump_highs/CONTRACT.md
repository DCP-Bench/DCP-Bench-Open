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
(`FEASIBILITY_SENSE`) is a satisfaction problem. The driver sets one thread, silence,
`mip_rel_gap = 0` and the time limit; only `OPTIMAL` counts as an answer.

## Compilation

None, but loading the packages and compiling the first solve take part of the execution
budget.

## Environment

Image `dcp-eval/jump_highs:v1`: Julia 1.12.7, JuMP 1.32.0, HiGHS.jl 1.26.0 (HiGHS_jll
1.15.1), JSON 1.10.0, pinned in [Manifest.toml](Manifest.toml) and precompiled into a
read-only depot; no network.

## Traps

- With `solution_limit > 1`, every variable under an output (directly or inside an
  expression) must be `Int` or `Bin` with finite lower and upper bounds; otherwise the
  driver reports `unsupported`. The no-good cut is a big-M built from those bounds.
- The no-good is over the variables an output is built from, not its value: an output
  expression over many variables makes the driver re-solve through every assignment
  with the same value. Declare such an output as its own bounded `Int` variable tied by
  an equality.
- The driver relays a `String` leaf unchanged; the old skill lists strings as an
  allowed output, but the generic contract rejects them.

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
