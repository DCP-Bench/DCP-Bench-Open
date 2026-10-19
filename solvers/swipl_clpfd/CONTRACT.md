# swipl_clpfd: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how SWI-Prolog
CLP(FD) expresses it. Runner: [run.py](run.py), which starts the driver
[driver.pl](driver.pl) in a separate `swipl` process and relays what it prints. The
driver consults the submission, calls `model/3` or `model/4`, owns labelling,
optimisation and enumeration, and prints the protocol records on stdout.

## Submission file

One Prolog file, `model.pl`, consulted into the same `user` module as the driver. It
loads what it uses itself (`:- use_module(library(clpfd)).`); the SWI-Prolog standard
library is available, no other file of yours is staged.

## Entrypoint

```prolog
model(+Instance, -Vars, -Outputs)              % satisfaction
model(+Instance, -Vars, -Outputs, -Objective)  % optimisation (preferred if both exist)
labeling_options(-Options)                     % optional, default [ff]
```

The driver calls the model once to prove the optimum (when `model/4` exists) and once
more to enumerate. `Vars` is the finite-domain variables to label; the driver labels
`term_variables(Vars-Outputs)`, so nesting is fine and output variables are always
labelled. `labeling_options/1`, if defined, must give a list of clpfd `labeling/2`
options without `min/1` or `max/1`. A `model/3`/`model/4` that fails is reported as
`unsat`.

## Instance

`Instance` is the instance JSON as a **dict** (`json_read_dict` with
`value_string_as(atom)`): read a field with `Instance.n` or `get_dict(n, Instance, N)`;
a capitalised name needs quotes, `get_dict('N', Instance, N)`. Values:

- integers and floats as numbers;
- JSON `true` / `false` / `null` as the **atoms** `true` / `false` / `null` (test with
  `== true`);
- **strings as atoms** (`atom_chars/2` or `atom_codes/2` take one apart);
- arrays as Prolog lists, ragged allowed, with no inherent index base: use `nth1/3` or
  `nth0/3` consistently, and remember `element/3` is 1-based;
- nested objects as dicts.

## Outputs

`Outputs` is a **nonempty list of `Name-Value` pairs**, one per declared output, with
`Name` an atom (`'A'-Xs` for a capital). `Value` is an integer, a variable, or a nested
list of these to the declared shape. Every variable still free in `Outputs` is labelled,
so it needs a finite domain: an output variable with an infinite one (`Y #> X` alone
gives `Y in 1..sup`) makes `labeling/2` raise an instantiation `error`. The driver writes the pairs with `json_write_dict`: integers as numbers, lists
as arrays, the atoms `true`/`false` as JSON Booleans, any other atom as a JSON string
(which the evaluator rejects). A repeated name is an `error`. Solutions whose output
object repeats one already printed are dropped.

## Objective

The fourth argument of `model/4` is `min(Expr)`, `max(Expr)` or `none`, with `Expr` a
clpfd arithmetic expression. The driver runs `once(labeling([min(Expr)|Options], Vars))`
(or `max`) and evaluates `Expr` with `is/2` on that first solution, so after labelling
`Vars` and the outputs every variable in `Expr` must be bound: labelled, or fixed by
propagation (`Z #= X + Y` with `X`, `Y` labelled is fine). Anything else in that
position is an `error`.

## Solving

- Labelling options are `labeling_options/1` when defined, else `[ff]`; the driver adds
  only the objective option. It labels `term_variables(Vars-Outputs)`.
- Optimum phase: `once(labeling([min(Expr)|Options], Vars))` (or `max`); clpfd reports
  solutions in objective order, so the first is the optimum. Failure there, or a model
  that fails, is `unsat`.
- Enumeration phase: the model is rebuilt, `Expr #= Optimum` is posted, and the driver
  backtracks into `labeling(Options, Vars)`; nothing else is added. A solution whose
  output object repeats one already printed is dropped. It stops at `limit` once enough
  distinct ones are out; when backtracking fails the search is exhausted (`complete`
  after a solution, `unsat` before).
- The time budget is `execution_timeout` from when the driver reads the request: each
  phase runs under `call_with_time_limit` with what is left, and running out is
  `timeout`. `run.py` kills a driver still silent 4 s past the budget (`timeout`).

## Compilation

No separate step. The file is consulted at run time, inside the execution budget
(`execution_timeout`, enforced by `call_with_time_limit` around each phase, with a 4 s
backstop kill in `run.py`); `compilation_timeout` does not apply. The process runs with
`--stack-limit=1g`.

## Environment

Image `dcp-eval/swipl_clpfd:v1`: the official `swipl:9.2.9` image (SWI-Prolog 9.2.9,
`swipl` on `PATH` at `/usr/bin/swipl`), with its full standard library, including
`library(clpfd)` and the JSON library `library(http/json)` (which the driver has already
loaded); the runner around it is that image's Python 3.11.2. `swipl` runs with
`--stack-limit=1g`; no environment variables are set for it. The evaluator runs the
container with no network, a read-only root file system, user 65534, `HOME=/tmp`, a
512 MiB writable `/tmp` and `/input` read-only. For an ad hoc run, override the
entrypoint: `docker run --rm --network none --entrypoint sh dcp-eval/swipl_clpfd:v1 -c
'swipl ...'`.

## Traps

- **Put every auxiliary variable in `Vars`** unless labelling `Vars` and the outputs
  fixes it by propagation. Only those are labelled; a constraint on an auxiliary left
  free only has to stay consistent, so a reported solution can violate it
  (`invalid_solution`). A variable that appears only in the objective `Expr` and is
  left free makes `is/2` raise, and the run is an `error`.
- **Never print.** stdout is the protocol: any non-JSON line (from `format/2`, `write/1`,
  a directive at load time) makes the run an `error`.
- **`labeling_options/1` must not hold `min/1`/`max/1`** and must be a list; the
  objective belongs to `model/4`.
- **Keep the model deterministic**: enumeration backtracks through `labeling/2` and then
  into `model/3,4`; leftover choice points would build and report a different model.
- The driver's own predicates live in the same module (`run/0`, `solve/5`, `build/4`,
  `search/5`, `optimum/3`, `enumerate/6`, `record/1`, `status/2`, `report/1`, ...). Do
  not define predicates with those names and arities.
- A syntax error does not stop the consult: the clause is skipped with a message on
  stderr, which typically surfaces as "defines neither model/3 nor model/4" or `unsat`.
- An output value may be the atom `true` or `false`: `json_write_dict` writes it as a
  JSON Boolean, which is accepted. `0`/`1` works as well.

## Example

The pilot fixture [tests/fixtures/model_swipl.pl](../../tests/fixtures/model_swipl.pl)
(instance fields `n`, `optimize` (arriving as the atom `true`/`false`); outputs `x`, `y`):

```prolog
:- use_module(library(clpfd)).

model(Instance, [X, Y], [x-X, y-Y], Objective) :-
    N = Instance.n,
    [X, Y] ins 0..N,
    (   Instance.optimize == true
    ->  X + Y #>= N,
        Objective = min(X + Y)
    ;   X + Y #= N,
        Objective = none
    ).
```
