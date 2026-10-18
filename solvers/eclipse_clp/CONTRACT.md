# eclipse_clp: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how ECLiPSe
expresses it. Runner: [run.py](run.py), which converts the instance, starts the driver
[driver.ecl](driver.ecl) in a separate `eclipse.exe` process and relays what the driver
wrote. The driver compiles the submission, calls `model/3` or `model/4`, owns labelling,
optimisation and enumeration, and writes the protocol records to a file of its own.

## Submission file

One ECLiPSe file, `model.ecl`, compiled into module `user` with `compile/1`, the same
module as the driver. It loads what it uses itself (`:- lib(ic).`, `:- lib(gfd).`); the
ECLiPSe libraries of the image are available, no other file of yours is staged. Load one
finite-domain solver per model: `ic` (bounds propagation on integers and reals) or `gfd`
(Gecode, integers only). The driver loads no solver library for you.

## Entrypoint

```prolog
model(+Instance, -Vars, -Outputs)              % satisfaction
model(+Instance, -Vars, -Outputs, -Objective)  % optimisation (preferred if both exist)
search_goal(+Vars)                             % optional, default labeling(Vars)
```

The driver calls the model once to prove the optimum (when `model/4` exists) and once
more to enumerate. `Vars` is the list of variables to label. After the labelling goal the
driver also labels every variable still free in `Outputs` (and in the objective) with
`labeling/1`, so output variables are always bound. `search_goal/1`, if defined, replaces
the default labelling of `Vars`; it is where `search/6` goes, for example
`search_goal(Vars) :- search(Vars, 0, first_fail, indomain_min, complete, []).` It must be
a complete search and must not call `bb_min`, `minimize` or any optimisation of its own.
A `model/3` or `model/4` that fails is reported as `unsat`. Predicates named `dcp_*` belong
to the driver; do not define them.

## Instance

`Instance` is a **list of `Key-Value` pairs** with an atom key per JSON field; read a field
with `memberchk(n-N, Instance)` (a missing field makes `memberchk` fail, so the model
fails and the run is `unsat`). Values:

- integers (bignums included) and floats as numbers;
- JSON `true` / `false` / `null` as the atoms `true` / `false` / `null`; match them in the
  pair, `memberchk(optimize-true, Instance)`;
- **strings as ECLiPSe strings** (`"abc"`, type `string/1`), counted in UTF-8 bytes by
  `string_length/2`, not in characters;
- arrays as lists, ragged allowed, with the JSON's 0-based positions and no inherent index
  base: `nth0/3` and `nth1/3` live in `lib(listut)` (`lib(lists)` does not have them), and
  `element/3` of `ic` and `gfd` is 1-based;
- nested objects as lists of `Key-Value` pairs, so an empty object and an empty array both
  arrive as `[]`.

## Outputs

`Outputs` is a **nonempty list of `Name-Value` pairs**, one per declared output, with
`Name` an atom (`'A'-Xs` for a capital) and no name repeated. `Value` is an integer, a
variable, the atom `true` or `false`, or a nested list of these to the declared shape.
The driver writes integers as JSON numbers, `true`/`false` as JSON Booleans, and lists as
arrays; `0` and `1` work as Booleans too. Anything else (a float, an interval such as
`0.0__0.0` from `$=`, a string, another atom) is an `error` naming the output. A value must
be ground after labelling. Solutions whose output values repeat one already reported are
dropped.

## Objective

The fourth argument of `model/4` is `min(Expr)`, `max(Expr)` or `none`, with `Expr` an
arithmetic expression of the solver library you loaded (`X + Y`, `sum(Xs)`, `max(A, B)`).
The driver posts `Cost #= Expr` (and `Neg #= -Cost` for `max`) in `user`, so the constraint
is the one your solver library defines, then minimises with `bb_min/3`. The cost must be
an integer once the variables are labelled; a real-valued objective is an `error`.

## Solving

- Optimum phase: `bb_min(Search, Cost, bb_options{strategy:continue, delta:1, factor:1})`
  with `Search` the labelling goal described above. Each solution must improve the cost by
  at least 1 until branch and bound exhausts the space, so the last solution is optimal;
  only then is it reported, as the first solution. A model that fails, or an optimum phase
  that finds nothing, is `unsat`.
- Enumeration phase (only when more than one solution is wanted and the optimum phase did
  not already reach the limit): the model is rebuilt, `Expr #= Optimum` is posted, and the
  driver backtracks through the labelling. Outputs equal to one already reported are
  skipped; it stops at `limit` once enough distinct ones are out, and when backtracking
  runs out it is `complete` after a solution and `unsat` before one.
- The time budget is `execution_timeout`, started when `run.py` starts. Each phase runs
  under `timeout/3` with what is left and running out is `timeout`; an unproven optimum
  never counts as a result. `run.py` kills a driver that is still running 4 s past the
  budget and reports `timeout`, since a long propagation inside Gecode does not see the
  alarm until it returns.
- The verdict is the driver's own status record, never the exit code: ECLiPSe exits with
  0 after errors.

## Compilation

No separate step. The file is compiled at run time, inside the execution budget;
`compilation_timeout` does not apply. A syntax error makes the run an `error` with
ECLiPSe's message (`syntax error: postfix/infix operator expected`, with the line).

## Environment

Image `dcp-eval/eclipse_clp:v1`: `python:3.12.11-slim-trixie` with the ECLiPSe 7.2 basic
binary distribution (release build 7.2_13, `eclipse_basic.tgz`) unpacked in `/opt/eclipse`,
binary `/opt/eclipse/lib/x86_64_linux/eclipse.exe`, with `ECLIPSEDIR=/opt/eclipse` and
`LD_LIBRARY_PATH=/opt/eclipse/lib/x86_64_linux`. It starts as
`eclipse.exe -f /opt/runner/driver.ecl -e dcp_main`. Libraries that load: `ic`,
`ic_global`, `gfd` (Gecode 6.2.0), `fd`, `branch_and_bound`, `timeout`, `lists`,
`listut`. `eplex` loads but has no LP solver behind it (its OSI/CBC part fails), so do not
use it. There is no JSON library: the instance is already a term. Files the process uses
under `/tmp`: `dcp_request.ecl`, `dcp_protocol.jsonl`, `dcp_messages.txt`,
`dcp_stdout.txt`. The evaluator runs the container with no network, a read-only root file
system, user 65534, `HOME=/tmp`, a 512 MiB writable `/tmp` and `/input` read-only. For an
ad hoc run, override the entrypoint: `docker run --rm --network none --entrypoint
/opt/eclipse/lib/x86_64_linux/eclipse.exe dcp-eval/eclipse_clp:v1 -f /w/file.ecl -e halt`
(use `halt/0`; `halt/1` is undefined).

## Traps

- **ECLiPSe aborts on an error.** Its default error handler prints the message and
  aborts, so the run is an `error` whose detail is the last 2000 characters of the
  messages (for example `calling an undefined procedure foo(_956) in module user`,
  `instantiation fault in atom_length(_, _)`). Singleton-variable warnings go to the same
  place and show up in that text; they are harmless. A thrown ball that is not `abort` is
  reported as `The submission threw <ball>`.
- **Printing is harmless but useless.** The protocol goes to a file, so `writeln/1` and
  library load messages (`Loaded Gecode solver 6.2.0`) cannot corrupt it; they are
  forwarded to stderr only.
- **`gfd` integers are 32-bit.** A bound beyond about 2^31 empties the domain and the model
  silently fails (`unsat`). `ic` bounds are floating point: constraints are exact only up
  to 2^53, but plain arithmetic with `is/2` is exact for bignums. Declare wide outputs as
  plain integers computed with `is/2`, or use digits.
- **`ic` and `ic_global` both export `alldifferent/1`.** Loading both gives `Ambiguous
  import of alldifferent / 1 from [ic, ic_global]` and the call is undefined. `ic` has
  `alldifferent/1` itself; qualify the call or load only one.
- **`gfd` has its own operators**: reified constraints use `<=>`, `=>`, `and`, `or`, `neg`
  between constraints, and `#<=>` is a syntax error there.
- **Free auxiliary variables are not labelled.** Put every auxiliary variable in `Vars`
  unless labelling `Vars` and the outputs fixes it by propagation. Variables free in the
  outputs or in the objective expression are labelled with `labeling/1` after your search
  goal, which ignores your heuristic for them; a free auxiliary in `Vars` is labelled by
  your goal and handled by the output deduplication.
- **Keep the model deterministic.** Enumeration backtracks through the labelling and then
  into `model/3,4`; a leftover choice point rebuilds and re-reports the same model.
- **`**` is not an operator** (`2**70` is a syntax error); use `^`.
- **A solver library is needed to label.** A model of plain arithmetic with `Vars = []`
  works without any; otherwise the driver calls `labeling/1` in `user`, so a model that
  loads no solver fails with `calling an undefined procedure labeling(...)`.
- **The `lists` library is small.** `flatten/2`, `append/3`, `delete/3`, `reverse/2`,
  `sum/2` and `memberchk/2` are there; `nth0/3`, `nth1/3`, `last/2` and `sumlist/2` need
  `lib(listut)`. Declarative `foreach ... do` loops need no library.
- The driver's own state lives in `user` (`dcp_main/0`, `dcp_*` predicates and the
  `dcp_count`, `dcp_seen` variables); `model/3`, `model/4` and `search_goal/1` are the
  only names it reads from you.

## Example

The pilot fixture [tests/fixtures/model_eclipse.ecl](../../tests/fixtures/model_eclipse.ecl)
(instance fields `n`, `optimize` (arriving as the atom `true`/`false`); outputs `x`, `y`):

```prolog
:- lib(ic).

model(Instance, [X, Y], [x-X, y-Y], Objective) :-
    memberchk(n-N, Instance),
    [X, Y] #:: 0..N,
    (   memberchk(optimize-true, Instance)
    ->  X + Y #>= N,
        Objective = min(X + Y)
    ;   X + Y #= N,
        Objective = none
    ).
```
