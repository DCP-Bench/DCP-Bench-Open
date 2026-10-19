# picat: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Picat
expresses it. Runner: [run.py](run.py), which writes the instance as a Picat term and
starts the driver [driver.pi](driver.pi) in a separate `picat` process. The driver loads
the submission, calls `model/4`, owns search, optimisation and enumeration, and writes
the protocol records to a file, never to stdout.

## Submission file

One Picat file, `model.pi`. It must **import exactly one solver module, `cp` or `sat`**;
the driver solves with whichever one is loaded. Other library modules (`import util.`)
are fine. No other file of yours is staged.

## Entrypoint

```picat
model(Data, Vars, Outputs, Options) => ...
```

The driver calls `model/4` with `Data` bound and the other three unbound, once to prove
the optimum and once more to enumerate (the model is rebuilt from scratch each time).
`Vars` is the decision variables to label (a list, array, or nested lists/arrays). The
driver labels every variable in `Vars` first, in that order, then any still free in
`Outputs` or the objective; under `cp` it finally labels whatever remains in suspended
constraints (`solve_suspended`). A `model/4` that fails is reported as `unsat`.

## Instance

`Data` is a Picat **map**. Keys are atoms: `Data.get(n)`, and `Data.get('N')` or
`Data.get('_SHIP')` with quotes for a name starting with a capital or underscore. Values:

- integers as integers, floats as floats;
- JSON `true` / `false` as **`1` / `0`** (Picat has no Boolean type);
- strings as Picat strings (lists of one-character atoms); a string holding a control
  character other than newline or tab is refused (`error`);
- arrays as **lists, indexed from 1** (`Grid[2,1]` is row 2, column 1 of a list of
  lists); ragged lists are fine;
- nested objects as maps, `null` as the atom `null`.

## Outputs

`Outputs` is a **nonempty list of `Name = Value`** pairs (or a map), one per declared
output. `Name` is an atom (`'A' = Xs` for a capital) or a nonempty string. `Value` is an
integer, a domain variable, or a list or array of these nested to the declared shape; a
2-D array from `new_array(R, C)` is written as a list of rows. A value still unbound after
labelling is an `error`. A declared Boolean is an integer `0`/`1`; an atom, string or
float is serialised (as a JSON string or float) but then rejected by the evaluator. The
driver drops a solution whose output object repeats one already reported.

## Objective

Put at most one objective in `Options`, written with `$`: `$min(Obj)` or `$max(Obj)`,
where `Obj` is a variable or an expression (the driver ties an expression to a fresh
variable with `#=`). Everything else in `Options` (e.g. `ff`, `split`) is passed to
`solve/2`; `Options` must be a list, `[]` for satisfaction.

## Solving

- The driver adds no solve options of its own: it calls `solve(Options, LabelVars)` of
  the imported module (`cp` or `sat`) with the submission's `Options`, plus the
  objective option in the first phase. Under `cp` it then runs
  `once(solve_suspended([]))` on each solution.
- Optimum phase: `once(solve([$min(V)|Options], LabelVars))`; both modules return the
  first solution only once it is proven optimal. Failure there is `unsat`.
- Enumeration phase: the model is rebuilt, `V #= Optimum` is posted, and the driver
  backtracks into `solve/2` for the next labelling of `LabelVars`; nothing else is added.
  A solution whose output object repeats one already reported is dropped. It stops at
  `limit` once enough distinct ones are out; when backtracking fails the search is
  exhausted: `complete` after a solution, `unsat` for a satisfaction model with none (an
  optimum not found again is `error`).
- The time budget: `run.py` kills the `picat` process at `execution_timeout` less 1 s
  (and less the time it spent before starting it), keeps the solutions recorded so far,
  and reports `timeout`. A `picat` exit without a status record is `error`.

## Compilation

No separate step. The driver compiles the file with `cl/1` at run time, inside the
execution budget (`execution_timeout`, less a 1 s margin); `compilation_timeout` does not
apply. A syntax error is an `error` whose detail carries Picat's own message with the
line range.

## Environment

Image `dcp-eval/picat:v1`: the official Picat 3.9#12 64-bit Linux build (checksummed),
driven from Python 3.12.11 (standard library only). The binary is
`/opt/picat/picat` and is **not on `PATH`**; its library modules are in
`/opt/picat/lib` (`cp`, `sat`, `util`, `planner`, `ordset`, `datetime`, `math`, `os`,
...). Solver modules `cp` and `sat` are usable; `mip` and `smt` are present as modules
but have no external solver installed. Picat has no JSON library; a submission needs
none, because the instance arrives as a map and the driver writes the JSON. No
environment variables are set for Picat. The evaluator runs the container with no
network, a read-only root file system, user 65534, `HOME=/tmp`, a 512 MiB writable
`/tmp` and `/input` read-only. For an ad hoc run, override the entrypoint: `docker run
--rm --network none --entrypoint sh dcp-eval/picat:v1 -c '/opt/picat/picat ...'`.

## Traps

- **Import exactly one of `cp` and `sat`.** Neither, both, `mip` or `smt` is an `error`
  before any solving.
- **Write `$min(...)` / `$max(...)`**: without `$`, Picat calls the `min`/`max` function
  instead of building the option term. More than one objective option is an `error`.
- **Keep `model/4` deterministic**: define it with `=>`, not `?=>`, and leave no choice
  points in its body (a generating `member/2`, say). Enumeration backtracks through
  `solve/2` and then into `model/4`, and would report solutions of a second, different
  model.
- **`model/4` must give the same model on both calls**: no global state or randomness.
- Avoid predicate names starting with `dcp_`, and do not define `main/1`: the
  submission is loaded into the driver's program.
- Printing (`println`) is harmless but useless: stdout is relayed to stderr as a log.

## Example

The pilot fixture [tests/fixtures/model_picat.pi](../../tests/fixtures/model_picat.pi)
(instance fields `n`, `optimize` (arriving as `1`/`0`); outputs `x`, `y`):

```picat
import cp.

model(Data, Vars, Outputs, Options) =>
    N = Data.get(n),
    [X, Y] :: 0..N,
    if Data.get(optimize) == 1 then
        X + Y #>= N,
        Options = [$min(X + Y)]
    else
        X + Y #= N,
        Options = []
    end,
    Vars = [X, Y],
    Outputs = [x = X, y = Y].
```
