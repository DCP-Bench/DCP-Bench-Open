---
name: swipl-clpfd
description: SWI-Prolog CLP(FD), the finite-domain constraint solver in library(clpfd) of SWI-Prolog 9.x, for constraint satisfaction and optimisation in Prolog. Use when writing, debugging or explaining clpfd models, global constraints, labelling or optimisation in SWI-Prolog, or when the user has chosen SWI-Prolog for a puzzle, scheduling, assignment or counting problem.
license: Apache-2.0
compatibility: Requires SWI-Prolog 9.2 or later with its bundled library(clpfd) and library(time); tested with 9.2.9. Free and open source; no key or account.
metadata:
  domain: constraint-programming
  solver: SWI-Prolog CLP(FD)
  paradigm: clp
---

# SWI-Prolog CLP(FD)

Constraint logic programming over finite domains. Variables get domains, constraints are ordinary Prolog goals that propagate as they are posted, and `labeling/2` is the only search. Keep one rule in mind: **give every variable a finite domain before it is labelled, and list every variable whose value you need in the labelling.**

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Input and output](#input-and-output)
- [Modelling](#modelling)
- [Solving](#solving)
- [Scheduling](#scheduling)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)

| Runnable example (program and README in `assets/`) | Pattern |
|---|---|
| [satisfy-sudoku](assets/satisfy-sudoku/README.md) | one solution, `all_distinct/1`, givens |
| [all-solutions-coins](assets/all-solutions-coins/README.md) | all solutions with `findall/3` |
| [all-optimal-team](assets/all-optimal-team/README.md) | minimise, then all optimal solutions |
| [maximise-knapsack](assets/maximise-knapsack/README.md) | maximise a linear value |
| [minimise-assignment](assets/minimise-assignment/README.md) | minimise with `element/3` |
| [infeasible-pigeons](assets/infeasible-pigeons/README.md) | no solution, reported |
| [scheduling-makespan](assets/scheduling-makespan/README.md) | `cumulative/2`, precedences, minimise |

## Install

Docs: [SWI-Prolog download and install](https://www.swi-prolog.org/Download.html)

```bash
sudo apt-add-repository ppa:swi-prolog/stable   # Ubuntu: the PPA tracks releases
sudo apt-get update && sudo apt-get install swi-prolog
brew install swi-prolog                          # macOS, Homebrew
swipl -g "use_module(library(clpfd)), writeln(ok), halt"
```

The distribution package may be older than 9.2 ([Debian/Ubuntu notes](https://www.swi-prolog.org/build/Debian.md)). The last line prints `ok` when clpfd loads; check the version with `swipl --version`.

## Quick start

Save as `model.pl`, run `swipl model.pl`. It prints `X = 3, Y = 2`.

```prolog
:- use_module(library(clpfd)).
:- initialization(main, main).

main :-
    X in 0..5, Y in 0..5,
    X + 2*Y #= 7,
    X #> Y,
    labeling([], [X, Y]),
    format("X = ~w, Y = ~w~n", [X, Y]).
```

## Input and output

A model that reads an instance file takes the path from the command line and parses JSON with `library(http/json)`. Run it as `swipl model.pl inst.json`; `main/1` receives `['inst.json']`.

```prolog
:- use_module(library(clpfd)).
:- use_module(library(main)).        % library(main) calls main/1 with the arguments
:- use_module(library(http/json)).
:- initialization(main, main).

main(Argv) :-
    Argv = [File|_],
    setup_call_cleanup(open(File, read, In), json_read_dict(In, Inst), close(In)),
    get_dict(weights, Inst, Ws),       % keys are atoms; JSON arrays are Prolog lists
    length(Ws, N), length(Take, N), Take ins 0..1,
    % ... constraints and labelling ...
    json_write_dict(current_output, _{take: Take}, [width(0)]), nl.   % one JSON line
```

- `json_read_dict/2` gives a dict; `get_dict(Key, Dict, Value)` fails when the key is missing, and the model then fails rather than raising, so print the dict once when a key is in doubt.
- `json_write_dict/3` with `width(0)` writes one line. Write plain text with `format/2` instead when the output is not JSON.
- Labelled values are integers, and `format` shows an unlabelled variable as `_123`: print only after labelling.

## Modelling

Full list: [clpfd reference](https://www.swi-prolog.org/pldoc/man?section=clpfd)

| Need | API |
|---|---|
| domain of variables | `X in 1..9`, `Xs ins 0..N`, with a hole: `X in 1..3 \/ 7..9` |
| arithmetic relation | `#=` `#\=` `#<` `#=<` `#>` `#>=` over `+ - * // div mod rem abs min max ^` |
| all different | [`all_distinct/1`](https://www.swi-prolog.org/pldoc/man?section=clpfd) (domain-consistent, prefer it) · `all_different/1` (weaker) |
| linear sum | `sum(Xs, #=, E)` · weighted `scalar_product(Cs, Xs, #=, E)` |
| element at a variable index | `element(I, Xs, V)`: **1-based**, `I` may be a variable |
| value counts | `global_cardinality(Xs, [K-N, ...])`, `N` may be a variable |
| table of allowed tuples | `tuples_in([[X,Y], ...], Relation)` |
| successor circuit | `circuit(Succs)` |
| ordering | `chain(Xs, #=<)`, `lex_chain(Lists)` |
| no overlap on one machine | `serialized(Starts, Durations)` |
| cumulative resource | `cumulative(Tasks, [limit(L)])` with `task(Start, Duration, End, Resource, Id)` |
| no overlap in 2D | `disjoint2([f(X, W, Y, H), ...])` |
| automaton | `automaton(Xs, Nodes, Arcs)` |
| reification | `B #<==> (X #= V)` gives a 0/1 `B`; also `#==>`, `#<==`, `#\/`, `#/\`, `#\` |
| transpose a list of lists | `transpose(Rows, Columns)` |

There is no `nvalue/2` and no `count/4`: reify each test and `sum/3` the results, or use `global_cardinality/2`.

Patterns that come up often:

```prolog
% Rows and columns all different (a Latin square of size N).
latin_square(N, Rows) :-
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 1..N), Rows),
    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns).

% Count the entries equal to Value.
occurrences(Value, Xs, Count) :-
    maplist({Value}/[X, B]>>(X #= Value #<==> B), Xs, Bs),
    sum(Bs, #=, Count).

% The cell at a decision-dependent position: flatten, then element/3 (1-based).
cell(Rows, Width, I, J, V) :-
    append(Rows, Flat),
    Position #= (I - 1) * Width + J,
    element(Position, Flat, V).
```

**Pitfalls:** `=` unifies terms and posts nothing, while `#=` posts a constraint. `is/2` evaluates only ground arithmetic. `in` takes one variable and `ins` takes a list, so `Y ins 0..3` on a single variable raises `instantiation_error`. Domain bounds must be integers or bound variables: write `N1 is N-1, X in 0..N1` rather than `X in 0..N-1`, which raises `domain_error(clpfd_domain, ...)`. Lists of integers can be built with `numlist/3`, and summed with `sum_list/2`.

## Solving

Docs: [labeling/2 and its options](https://www.swi-prolog.org/pldoc/doc_for?object=labeling/2)

| Option category | Options (one per category; default in bold) |
|---|---|
| variable choice | **`leftmost`**, `ff`, `ffc`, `min`, `max` |
| value choice | **`up`**, `down` |
| branching | **`step`**, `enum`, `bisect` |
| random order | `random_variable(Seed)`, `random_value(Seed)`: a fixed seed repeats the run |
| optimisation | `min(Expr)`, `max(Expr)` (see below) |

Choose the labelling order as part of the model: `ff` has nothing to go on when every variable has the same domain size, as in a Boolean matrix. Put the variables that constrain most first (the heaviest item, the longest task) and select `leftmost`.

| Observed | Meaning |
|---|---|
| `labeling/2` succeeds | a solution; the variables are bound; backtrack for the next |
| `labeling/2` fails | no (more) solutions; a failing constraint post also means no solution |
| `error(instantiation_error, _)` | a labelled variable has no finite domain, or `is/2` met a constrained variable |
| `error(domain_error(consistent_labeling_options, Opts), _)` | two options from one category |
| `time_limit_exceeded` | raised by `call_with_time_limit/2` ([library(time)](https://www.swi-prolog.org/pldoc/man?section=time)) |

**Time limit and seed:** `call_with_time_limit(Seconds, Goal)` wraps a search and raises `time_limit_exceeded` when it runs out. A seed is set with `random_variable(Seed)` or `random_value(Seed)` in the options.

**Optimisation:** `labeling([min(Expr)], Vars)` returns the optimum first, and later solutions come in non-decreasing `Expr`. When `Vars` is labelled, `Expr` must become ground: a variable of `Expr` is fine if it is in `Vars` or the constraints fix it from `Vars` (`S #= 3 - R` with `labeling([max(S)], [R])` works), but a variable nothing fixes raises `instantiation_error` (`labeling([max(P+Q)], [P])` with `Q` free). Use `once/1` to take only the optimum.

A labelled optimum is proved before it is returned, so the first answer can take minutes on a hard model. For an answer you can report before the proof ends, use the bounded descent below: each round posts a bound, finds one solution under it, records it and tightens the bound. `build/3` (your model) creates fresh variables in each round, so the values an earlier round labelled do not constrain the new round.

```prolog
descend(Ws, Bound) :-
    build(Ws, Total, Vars),                     % your model: constraints, Total, Vars
    ( Bound == none -> true ; Total #=< Bound ),
    labeling([ff], Vars), !,
    V is Total,
    nb_setval(best, V),                         % the last value recorded is the incumbent
    Next is V - 1,
    descend(Ws, Next).
descend(_, _).                                  % no solution under the bound: the incumbent is optimal

% in main/1, a round limit of 60 s on the search:
nb_setval(best, none),
catch(call_with_time_limit(60, descend(Ws, none)), time_limit_exceeded, true),
nb_getval(best, Best).                          % none, or the best found; proven only if descend ended normally
```

Read the outcome: when `descend/2` ends by its second clause, `best` is optimal. When the time limit fires, `best` is the best found so far, which is not proven optimal, so say so in the output. The pattern was run on the jobshop ft06 instance: makespan 55 (the optimum) within 15 s, while the plain `labeling([min(Mk)], ...)` ran for about 300 s before it returned.

For maximisation, post `Total #>= Bound + 1` and recurse with `descend(V)`; the same loop gave the optimum 12 on a three-item knapsack.

**Reading values:** variables are integers only after labelling; before, `format` prints `_123`. `fd_dom(X, Dom)` shows the current domain.

**Where errors appear:** `format/2` and `writeln/1` write to stdout. Uncaught errors, warnings and syntax errors go to stderr. A syntax error skips one clause and loading continues, so the symptom is a later `Unknown procedure`. Under `initialization(main, main)` an uncaught error exits with status 2 and a failing `main` with status 1.

## Scheduling

Use `serialized(Starts, Durations)` for a machine that runs one task at a time (no overlap, a disjunctive resource), and `cumulative(Tasks, [limit(L)])` with `task(Start, Duration, End, Resource, Id)` when a resource holds up to `L` tasks at once. A job-shop model posts one `serialized/2` per machine and `S + D #=< S2` for each precedence inside a job; the tester's ft06 model did this and reached the optimum (55) with the descent in 15 s.

- Each makespan bound is `Mk #>= End` for every task end, and the precedences are inequalities between starts and ends.
- The descent above labels `ff` over the starts with the makespan last. With plain `labeling([min(Mk)], ...)` on ft06 the same model took about 300 s, so for a large instance use the descent to get an answer you can report.
- The full cumulative example is [scheduling-makespan](assets/scheduling-makespan/README.md).

## All solutions

```prolog
findall(Vars, labeling(Options, Vars), Solutions)
```

`findall/3` copies its template: it is safe after labelling because the copies are ground. Use it on ground data only, never to gather decision variables before they are constrained (see [Common issues](#common-issues)).

If the answer is only part of `Vars`, several labellings can give the same answer; remove the repeats with `sort/2`.

All **optimal** solutions: find the optimum, post it as a constraint, then enumerate again.

```prolog
team(Costs, Pick, Cost) :-           % Pick is a 0/1 list; Cost its linear total
    length(Costs, N), length(Pick, N), Pick ins 0..1,
    sum(Pick, #=, 3), scalar_product(Costs, Pick, #=, Cost).

main :-
    Costs = [3, 1, 4, 1, 3],
    team(Costs, Pick, Cost), once(labeling([min(Cost)], Pick)), Optimum is Cost,
    findall(P, (team(Costs, P, C), C #= Optimum, label(P)), Best).   % Best: 2 teams
```

Full program: [all-optimal-team](assets/all-optimal-team/README.md). Details: [enumeration](https://www.swi-prolog.org/pldoc/man?section=clpfd).

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `Arguments are not sufficiently instantiated` at labelling | a variable has no finite domain | post `in`/`ins` before labelling |
| same error from `is/2` | `is` used on a constrained variable | use `#=`; `is` only on ground terms |
| same error from `labeling([min(E)], ...)` | a variable of `E` is neither labelled nor fixed by the constraints | add it to the labelled list, or post the constraint that fixes it |
| `Domain error: clpfd_domain expected`, `found 0..N-1` | a domain bound is an expression, not an integer | `N1 is N-1`, then `X in 0..N1` |
| `instantiation_error` from `Y ins 0..3` | `ins` takes a list; `in` takes one variable | `Y in 0..3`, or `Ys ins 0..3` on a list |
| `Argv = [File|_]` fails, or the file is missing | the instance path was not passed after the script | run `swipl model.pl inst.json`; `main/1` gets the arguments after the script name |
| `get_dict/3` fails, so `main` fails with no output | the JSON key name differs from the one in the model | print the dict once and match the key names |
| optimum takes minutes, or `time_limit_exceeded` with no answer | `labeling([min(E)], ...)` proves the optimum before returning | use the bounded descent and print the incumbent, saying whether it is proven |
| answer ignores a constraint you can see | `=` used where `#=` was meant | `#=` posts the constraint |
| answer ignores constraints posted in a `findall/3` | `findall/3` copied the variables; the constraints hit copies | gather variables with `maplist` or recursion, which unify |
| lambda variable is fresh or unbound inside `[X]>>...` | an outer variable not in the `{...}` set | write `{N}/[X]>>...` for every outer variable used |
| reported values break a constraint on an auxiliary | an auxiliary is not labelled, so its constraint only stays consistent | label every auxiliary that carries a constraint |
| goal fails where a solution must exist | wrong arity, unbound `is`, list length mismatch | test each goal alone before blaming the constraints |
| `nth1/3` with a variable index enumerates | it is backtracking, not a constraint | use `element/3` over a flattened list |
| `Unknown procedure: maplist/6` | `maplist` is defined only up to `maplist/5` (a goal and four lists) | nest `maplist` or index the lists with `nth1/3` |
| `Unknown procedure: nvalue/2` or `count/4` | not part of clpfd | reification plus `sum/3`, or `global_cardinality/2` |
| `consistent_labeling_options` error | two options of one category | keep one per category |
| labelling takes too long | weak propagation or a poor order | `all_distinct` over `all_different`, an implied constraint, `ff`/`ffc`, a better order; for a scheduling model, `serialized/2` per machine and the bounded descent |
| a run ends without an answer under a time limit | the search was still proving or searching | report the incumbent, or no answer, and say it is not proven; a correct model can need several minutes |

## Further reading

- Documentation for agents: none found; start from the clpfd reference below.
- API reference: [library(clpfd)](https://www.swi-prolog.org/pldoc/man?section=clpfd), [labeling/2](https://www.swi-prolog.org/pldoc/doc_for?object=labeling/2)
- Examples: [library/clp/clpfd.pl](https://github.com/SWI-Prolog/swipl-devel/blob/master/library/clp/clpfd.pl) (the header comments carry SEND+MORE, Sudoku and N-queens)
