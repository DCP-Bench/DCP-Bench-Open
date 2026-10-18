---
name: eclipse-clp
description: ECLiPSe, the ECLiPSe Constraint Logic Programming system (version 7.x), for finite-domain constraint satisfaction and optimisation in Prolog syntax with libraries ic, ic_global, gfd (Gecode), branch_and_bound and timeout. Covers variables and domains, global constraints, reification, search, optimisation with bb_min, all solutions, timeouts and reading JSON data. Use when writing, debugging or explaining ECLiPSe models, or when the user has chosen ECLiPSe for a puzzle, scheduling, assignment or routing problem.
license: Apache-2.0
compatibility: Requires ECLiPSe 7.x from eclipseclp.org (tested with 7.2 #13, x86_64 Linux, libraries ic, ic_global, ic_edge_finder, ic_mdd, gfd, branch_and_bound, timeout, listut, json). Free and open source (MPL); no key or account.
metadata:
  domain: constraint-programming
  solver: ECLiPSe
  paradigm: clp
---

# ECLiPSe (CLP)

ECLiPSe is a Prolog system with constraint libraries. Variables get domains, constraints
propagate when posted, and search is Prolog backtracking. Rules to keep: **load the libraries
with directives at the top of the file, give every variable a finite domain, label every
variable whose value you need**, and **minimise through `bb_min/3` with a variable as cost**.
A failed goal means "no solution"; nothing is raised.

## Contents
- [Running](#running)
- [Libraries](#libraries)
- [Modelling](#modelling)
- [Global constraints](#global-constraints)
- [Search](#search)
- [Optimisation](#optimisation)
- [All solutions](#all-solutions)
- [Timeouts](#timeouts)
- [Reading data and printing](#reading-data-and-printing)
- [Choosing an encoding](#choosing-an-encoding)
- [Common issues](#common-issues)
- [Examples](#examples)

## Running

Download a build from [eclipseclp.org](https://eclipseclp.org/) and unpack it. The launcher
is `eclipse`; a plain tarball install can hold only the binary `eclipse.exe`, which needs
`ECLIPSEDIR` (the install directory) and `LD_LIBRARY_PATH` (`$ECLIPSEDIR/lib/x86_64_linux`).
Put it on `PATH` or call it by full path.

```bash
eclipse.exe -f model.ecl -e main            # load model.ecl, run the goal main/0, then stay in the toplevel
eclipse.exe -f model.ecl -e main -- a.json  # user arguments after --
```

With stdin at end-of-file (`</dev/null`) the toplevel ends after the goal. Put `halt` at the end
of `main` or redirect stdin. Exit codes are unreliable: read the output.
`argv(all, L)` inside the goal gives `[ProgramPath | UserArguments]` as strings.

```prolog
:- lib(ic).                       % directives run while the file loads
main :- X :: 1..9, X #> 3, X #< 6, labeling([X]), writeln(X).   % prints 4
```

A model is a file of clauses; `main/0` is the entry. Variables start with an upper-case letter
or `_`. Strings use double quotes; `printf("%d %w%n", [N, Term])` prints (`%d` integer, `%w` any
term, `%n` newline). Call `lib/1` as a directive, never inside a clause body (the operators
it adds must exist when the clauses are read).

## Libraries

| Library | Gives |
|---|---|
| `ic` | integer and real interval constraints `#=`, `#\=`, `#<`, `#=<`, `#>`, `#>=`, `$=`; `::`, `labeling/1`, `indomain/1`, `search/6`; `alldifferent/1`, `element/3`, `circuit/1`; `sum/1`, `min/max` |
| `ic_global` | `alldifferent/1`, `atmost/3`, `occurrences/3`, `lex_le/2`, `sorted/2`; also exported, not run here: `alldistinct/1`, `ordered/2`, `nvalue/2`, `bin_packing/3`, `alldifferent_matrix/1` |
| `ic_mdd` | `table/2` for `ic` (also re-exported by `ic_global_gac`) |
| `ic_global_gac` | `gcc/2` and other GAC versions of the globals |
| `ic_edge_finder`, `ic_edge_finder3` | `disjunctive/2`, `cumulative/4`: the strongest propagation for scheduling |
| `ic_cumulative`, `cumulative` | `cumulative/4` with weaker propagation |
| `gfd` | the Gecode solver, replaces `ic`: `::`, `#=` and the globals `alldifferent/1`, `gcc/2`, `table/2`, `cumulative/4`, `disjunctive/2`, `circuit/1`, `element/3`, `regular/2`, `count/4`, `bin_packing/3`; integers within about 32 bits |
| `branch_and_bound` | `bb_min/3`, `minimize/2` |
| `listut` | `nth0/3`, `nth1/3` and more list predicates |
| `timeout` | `timeout/3` |
| `json` | `json_read/3`, `json_write/3` |
| `ic_sets`, `fd` | set variables; the older `fd` solver (`:: ` plus `#=`). Not used in this skill |

The programs here load either `ic` or `gfd`. Loading `ic` and `ic_global` together makes
`alldifferent/1` ambiguous. Resolve it with the import below; the same import works for any
name both libraries export.

```prolog
:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.
```

Under `gfd`, `gcc/2`, `table/2`, `cumulative/4`, `disjunctive/2` and `circuit/1` are part of `gfd`
itself; do not load `ic_global` there.

## Modelling

Docs: [ic library](https://eclipseclp.org/doc/bips/lib/ic/index.html), [gfd library](https://eclipseclp.org/doc/bips/lib/gfd/index.html).

| Need | Syntax |
|---|---|
| domain of one variable | `X :: 1..9`, or a list `[1,3,5]` for chosen values |
| the same domain on a list | `Xs :: 0..1` |
| list of fresh variables | `length(Xs, N), Xs :: 1..N` |
| array | `dim(M, [N,N]), M[1..N,1..N] :: 1..NN`; cell `X is M[I,J]` |
| array to list | `flatten_array(M, Flat)` (all cells); `collection_to_list(M[I,1..N], Row)` (one row); on a whole 2-D array it gives a list of row arrays |
| arithmetic | `X #= Y + 2*Z`, `X #\= Y`, `X #< Y`, `#=<`, `#>`, `#>=`; operators `+ - * // mod abs min max`, `sum(List)`, `max(List)`, `min(List)`, `^` |
| reals | `X $= 3 / 2` gives the interval `1.5__1.5`; `X :: 0.0..10.0, X * 2 $= 7` gives `3.5__3.5` (`ic` only) |
| loop over a list | `( foreach(X, Xs) do Goal )`; two lists in step: `( foreach(X, Xs), foreach(Y, Ys) do ... )` |
| build a list in a loop | `( foreach(X, Xs), foreach(T, Ts) do T = W*X )`: the second `foreach` is the output |
| integer loop | `( for(I, 1, N) do ... )`, `count(I, 1, _)`, nested `multifor([I,J], 1, [N,M])` |
| accumulate | `( foreach(X, Xs), fromto(0, A, B, Total) do B is A + X )` |
| outer variables in a loop | list every variable the body shares with the clause in `param(V1, V2)` |
| reification | `B #= (X #> 5)`, or `(X #> 5) => (Y #> 3)`, `<=>`, `or`, `and`, `neg` |
| value of a fixed variable | `Y is X + 1` works only once `X` is a number; use `#=` while `X` is open |

Constraints posted inside a `do` loop stay. A failure-driven loop (`member(...), post, fail`)
undoes everything it posted.

`#<=>`, `#\/` and `#/\` are not operators in `ic` or `gfd` (syntax error). Use `<=>`, `or`, `and`, `neg`,
`=>`. `**` is not an operator either: write `2^70`. In `ic`, `2^70` gives a bound interval
`1180591620717411172352 .. 1180591620717411565568`, not an exact integer: `ic` keeps bounds as
floats beyond 2^53, so large products are not exact.

Reading a domain: `get_var_bounds(X, Lo, Hi)` returns floats in `ic` (`4.0 - 9.0`);
`get_integer_bounds(X, Lo, Hi)` in `ic` and `get_bounds(X, Lo, Hi)` in `gfd` return integers (`4 - 9`);
`get_domain_as_list(X, L)` gives `[4,5,6,7,8,9]`. A variable that was not labelled prints as
`_123{2 .. 9}`.

## Global constraints

Every name and arity below was run.

| Constraint | Call | Library |
|---|---|---|
| all different | `alldifferent(Xs)` | `ic`, `ic_global`, `gfd` |
| element, 1-based | `element(I, List, V)` | `ic`, `gfd` |
| occurrences, at most | `occurrences(Val, Xs, N)`, `atmost(N, Xs, Val)` | `ic_global` |
| global cardinality | `gcc([gcc(Lo,Hi,Val), ...], Xs)` | `ic_global_gac`; in `gfd` the specs are `gcc{low:Lo,high:Hi,value:Val}` |
| table | `table([[A,B]], Rows)` (list of variable tuples, list of allowed rows) | `ic_mdd`; in `gfd` `table(Vars, Rows)` takes one flat tuple `[A,B]` |
| cumulative | `cumulative(Starts, Durations, Demands, Limit)` | `ic_edge_finder`, `ic_cumulative`, `gfd` |
| no overlap | `disjunctive(Starts, Durations)` | `ic_edge_finder`, `gfd` |
| circuit | `circuit(Succ)`: one cycle over all, 1-based successors | `ic`, `gfd` |
| lexicographic | `lex_le(Xs, Ys)` | `ic_global` |
| sorted | `sorted(Xs, Ys)` | `ic_global` |

`circuit/1` allows a self loop: post `Next[I] #\= I` for tours. `element/3` indexes from 1.

## Search

`labeling(Xs)` tries variables in order, smallest value first. `indomain(X)` labels one variable.
`search(Vars, Arg, Select, Choice, Method, Options)` in `ic` and `gfd` chooses the order:

| Argument | Values used |
|---|---|
| `Arg` | `0` for a list of plain variables |
| `Select` | run: `input_order`, `first_fail` (smallest domain), `anti_first_fail`, `smallest` (smallest lower bound). Documented, not run: `largest`, `occurrence`, `most_constrained`, `max_regret` |
| `Choice` | run: `indomain_min`, `indomain_max`, `indomain_split`. Documented, not run: `indomain_median`, `indomain_random`. `indomain_middle` fails in `gfd` |
| `Method` | `complete` for the full tree; limited-discrepancy and bounded-backtrack methods exist |

Effect on speed is in [Choosing an encoding](#choosing-an-encoding). Pick `first_fail` for
puzzles and `smallest` with `indomain_min` for scheduling start times, and measure.

## Optimisation

`bb_min(Goal, Cost, Options)` in `lib(branch_and_bound)` finds a solution of `Goal`, then
restarts or continues with a tighter bound on `Cost` until none exists. `Cost` must be a
**variable** (`type error in bb_min(...)` for an expression such as `X+1`): post `Cost #= Expr` first.
Maximise by minimising a negated variable. When `bb_min` exits normally the variables hold the
best solution and the optimum is proven, unless `timeout` was set in the options.

```prolog
:- lib(ic).
:- lib(branch_and_bound).
main :-
    X :: 0..10, Y :: 0..10, X + 2*Y #=< 14, Cost #= -(3*X + 2*Y),
    bb_min(search([X,Y], 0, input_order, indomain_max, complete, []), Cost,
           bb_options{report_success:true/0, report_failure:true/0}),
    printf("%d %d %d%n", [X, Y, Cost]).
```

| Option | Effect |
|---|---|
| `report_success:true/0`, `report_failure:true/0` | silence the `Found a solution with cost ...` lines that go to stdout by default |
| `strategy:continue` (default), `restart`, `step`, `dichotomic` | how the bound moves; `dichotomic` bisects the cost range. Equal speed on the 7x7 job shop measured below |
| `delta:D` | a new solution must improve by at least `D` (default 1.0); use a smaller value for fractional costs |
| `timeout:Secs` | stop after that time, exit normally with the best found, print `Branch-and-bound timeout while searching for solution better than N`; the optimum is not proven |
| `solutions:all` | backtrack through every optimal solution |
| `report_timeout:mark/0` | hook so the model can record that the run was cut |

To tell a proven optimum from a cut run, set `timeout` together with a `report_timeout` hook that sets
a flag, or run the search under an external time limit. `minimize/2` is the short form; it was not run here.

## All solutions

```prolog
findall(Xs, ( model(Xs), labeling(Xs) ), All)    % label only the decision variables; copies are ground
```

Label inside the goal: `findall` copies the variable and its constraints. For all optimal
solutions use `bb_options{solutions:all}` inside `findall`, or find the optimum first and
enumerate under `Cost #= Opt`. `once(Goal)` keeps the first solution. Examples:
[all-solutions-queens](assets/all-solutions-queens/README.md), [all-optimal-team](assets/all-optimal-team/README.md).

## Timeouts

`lib(timeout)`: `timeout(Goal, Seconds, TimeoutGoal)` runs `TimeoutGoal` when the time is up.
With `ic` a 2 s limit on a 40-queens `labeling` stopped as expected. With `gfd` a 100-queens
`search/6` wrapped in `timeout/3` with a 2 s limit was still running after more than 2 minutes
(the Gecode search is not interrupted; a magic-square N=6 run ignored a 60 s limit the same way).
**With `gfd`, impose the limit from outside** (an operating-system `timeout` on the process).
For `bb_min` use the `timeout` option.

## Reading data and printing

```prolog
:- lib(json).
% excerpt of the data-assignment example
read_rows(Rows) :- open("data.json", read, S), json_read(S, {Members}, [names_as_atoms]), close(S),
                   memberchk(cost:Rows, Members).
% ... and at the end of main:
%   printf("total %d, task %w\n", [T, Task]).
```

`json_read/3` with `names_as_atoms` returns an object as `{[key:Value, ...]}`, arrays as lists,
strings as strings. Unused keys are ignored with `memberchk`. `json_write/3` (with `indent(0)` for one line) writes JSON.
Example: [data-assignment](assets/data-assignment/README.md). `gfd` prints `Loaded Gecode solver 6.2.0`
on stdout at first use.

## Choosing an encoding

All numbers measured with ECLiPSe 7.2 #13 (cputime inside the system; wall adds 0.28 s start-up).

| Model | Variant | Time |
|---|---|---|
| 8-queens, all 92 solutions | `ic`, decomposed `#\=` | about 0.3 s wall |
| 10-queens, all solutions | `ic` decomposed / `ic` with `alldifferent` triple | 0.03 s / 0.65 s |
| 12-queens, all solutions | `ic` decomposed / `ic` with `alldifferent` / `gfd` decomposed / `gfd` with `alldifferent` | 0.80 / 16.25 / 0.99 / 1.14 s |
| queens, first solution, `first_fail` | `ic` N=100 / N=200 | 0.01 / 9.2 s |
| | `gfd` N=100 / N=200 | 0.04 / 2.52 s |
| | `ic` with `alldifferent`, N=60 / `gfd` with `alldifferent`, N=100 | over 60 s / 0.00 s |
| queens N=30, `input_order` | `ic` / `gfd` | over 60 s / 55.7 s |
| magic square, first solution, `first_fail` | `ic` N=5: `alldifferent` 0.04 s, decomposed 0.01 s | |
| | `ic` N=6: `alldifferent` 3.96 s, decomposed 1.17 s; N=7 both over 60 s | |
| | `gfd` N=4, 5: 0.00 to 0.02 s; N=6 did not finish | |
| job shop ft06 (6x6, optimum 55), `bb_min`, `smallest`/`indomain_min` | `ic_edge_finder` `disjunctive/2` / `ic_edge_finder3` | 0.01 / 0.01 s |
| | `ic_edge_finder` `cumulative/4` limit 1 | 0.01 s |
| | `ic_cumulative` `cumulative/4` limit 1, pairwise reified `or` | no proof in 120 s |
| random 7x7 job shop (optimum 56), `disjunctive/2` | `smallest`/`indomain_min` 0.92 s; `input_order` 4.36; `first_fail` 0.34; `smallest`/`indomain_max` 4.76; `smallest`/`indomain_split` 0.93; `anti_first_fail` 15.55 | |
| | `restart` 0.94, `dichotomic` 0.93; `ic_edge_finder3` 0.01; `ic_edge_finder` `cumulative/4` 0.38; `ic_cumulative` and pairwise over 60 s | |
| 8x8 job shop (seed 7) | `ic_edge_finder3` `first_fail` 0.05 s; `ic_edge_finder3` `smallest`, `ic_edge_finder` `first_fail` and `cumulative/4` `first_fail` over 60 s | |
| 10x10 job shop | no proof in 60 s; `bb_options{timeout:5}` returned 90 | |

What follows from the numbers:
- **Decomposed `#\=` beat `alldifferent` in `ic` on queens and magic squares** (12-queens 0.80 against 16.25 s). In `gfd` the two were close.
- **`gfd` goes further on first solutions** (queens N=200 in 2.52 s against 9.2 s) and with `alldifferent`.
- **Scheduling: `disjunctive/2` or `cumulative/4` from `ic_edge_finder`**, not `ic_cumulative` and not pairwise `or`.
- **Search order decides heavy-tailed scheduling runs**: `first_fail` was best on 7x7 and on one 8x8, and the same order timed out on another 8x8 with a different propagator. Try two orders and cut with `bb_options{timeout:T}`.
- `strategy:restart` and `dichotomic` did not change the 7x7 time.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `Ambiguous import of alldifferent / 1 from [ic, ic_global] in module eclipse` (twice), then `calling an undefined procedure alldifferent(...) in module eclipse`, `abort` | `ic` and `ic_global` both export it | `:- import alldifferent/1 from ic_global.` |
| `calling an undefined procedure foo_bar(1) in module eclipse` then `abort` | misspelt name, or the library is not loaded (`nth0`/`nth1` need `lib(listut)`, `gcc/2` needs `ic_global_gac`, `table/2` needs `ic_mdd`) | load the library with a directive; an undefined call aborts the whole goal |
| `file m.ecl, line 3: syntax error: postfix/infix operator expected` at `2**70`, `#<=>`, `#\/` or `#/\` | not operators in `ic` or `gfd` | `2^70`, `<=>`, `or`, `and`; or `B #= (X #> 5)` |
| `Gecode exception: IntVar::IntVar: Attempt to create variable with empty domain`, `Error in external function in g_add_newvars_interval(..., 1, 0, 3000000000)` | `gfd` bounds are about 32 bits; `0..3000000000` is too large | keep every bound and product below 2^31, or use `ic` |
| `gfd` `Y #= X*2` with `X :: 0..2000000000` leaves `X` in `0..5000000`, `Y` in `0..10000000`, no error | a variable made by an expression gets a default bound of 10000000 | give the helper variable its domain first |
| `type error in bb_min(labeling([...]), _ + 1, bb_options(...))` | the cost is an expression | `Cost #= Expr`, pass `Cost` |
| `out of range in search([...], 0, input_order, indomain_middle, complete, [])` | `indomain_middle` is not a `gfd` choice | `indomain_min`, `indomain_max`, `indomain_split` |
| output shows `_376519{2 .. 9}` instead of numbers | variable not labelled | `labeling/1` or `search/6` on it |
| `ic` bound reads `1180591620717411172352 .. 1180591620717411565568` | large integers are not exact in `ic` | keep numbers below 2^53 or use `gfd` within its bound |
| `get_var_bounds` prints `4.0 - 9.0` | it returns floats | `get_integer_bounds/3` (`ic`), `get_bounds/3` (`gfd`) |
| `collection_to_list` on a 2-D array returns row arrays; `get_finite_integer_bounds` type error | not flat | `flatten_array/2` |
| `trying to redefine a built-in predicate` for `:- dynamic seed/1` | `seed/1` is built in | pick another name |
| constraints vanish after a loop | failure-driven loop undid them | `( foreach(...) do ... )` |
| `findall` result has unlabelled variables | `findall` copies constraints | label before collecting |
| `Found a solution with cost ...` lines in the output | `bb_min` default reporting | `report_success:true/0, report_failure:true/0` |
| run with a `timeout/3` limit keeps going under `gfd` | the Gecode search is not interrupted | operating-system time limit |
| failure instead of a message | infeasible model, or a wrong constraint that fails | test with `( Goal -> ... ; ... )` |

## Examples

Each folder holds `model.ecl` and a README with the command and measured time. All run in about 0.3 s wall.

| Example | Pattern | Run |
|---|---|---|
| [satisfy-magic-square](assets/satisfy-magic-square/README.md) | arrays, `alldifferent`, sums | `eclipse.exe -f model.ecl -e main` |
| [all-solutions-queens](assets/all-solutions-queens/README.md) | `findall`, decomposed queens | same |
| [maximise-knapsack](assets/maximise-knapsack/README.md) | `bb_min` with a negated value | same |
| [minimise-jobshop](assets/minimise-jobshop/README.md) | `disjunctive/2`, minimise | same |
| [cumulative-schedule](assets/cumulative-schedule/README.md) | `cumulative/4`, minimise | same |
| [table-element-lex](assets/table-element-lex/README.md) | `table/2`, `element/3`, `lex_le/2`, `sorted/2` | same |
| [routing-tour](assets/routing-tour/README.md) | `circuit/1`, `element/3` | same |
| [infeasible-pigeonhole](assets/infeasible-pigeonhole/README.md) | infeasible | same |
| [data-assignment](assets/data-assignment/README.md) | JSON input and output | same, `-- other.json` for another file |
| [all-optimal-team](assets/all-optimal-team/README.md) | all optimal solutions | same |

Docs: [ECLiPSe documentation](https://eclipseclp.org/doc/), [library index](https://eclipseclp.org/doc/bips/lib/index.html).
