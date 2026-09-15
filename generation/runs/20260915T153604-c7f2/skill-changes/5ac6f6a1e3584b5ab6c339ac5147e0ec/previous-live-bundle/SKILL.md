---
name: swipl-clpfd
description: Write instance-agnostic SWI-Prolog CLP(FD) models for the DCP-Bench swipl_clpfd integration, covering the model/3 and model/4 submission contract, the clpfd constraints available in SWI-Prolog 9.2.9, and the mistakes that make a submission fail.
---

# SWI-Prolog CLP(FD) models for `swipl_clpfd`

Write one Prolog file that *states* a model. A driver inside the container
consults it, labels the variables, enumerates solutions and prints them. You
never call `label/1`, `labeling/2`, `write/1` or `format/2` yourself.

Image: SWI-Prolog 9.2.9 with `library(clpfd)`. `library(lists)`,
`library(apply)`, `library(yall)` and the rest of the SWI-Prolog standard
library are available; nothing else is installed and there is no network.

## The contract

```prolog
:- use_module(library(clpfd)).

% model(+Instance, -Vars, -Outputs)
model(Instance, Vars, [x-X, y-Y]) :-
    N = Instance.n,
    Vars = [X, Y],
    Vars ins 0..N,
    X + Y #= N.
```

- **`Instance`** is the instance JSON as a SWI-Prolog dict. `Instance.n` reads a
  field; `get_dict(n, Instance, N)` is the same thing written out, and is the
  form to use where dict functional notation is awkward (inside a `findall/3`
  goal, for example). JSON arrays arrive as lists, nested arrays as lists of
  lists, and JSON strings as atoms.
- **`Vars`** is a flat list of the finite-domain variables to label. Every
  variable still free in `Outputs` is labelled too, so an output variable no
  constraint mentions still gets a value.
- **`Outputs`** is a nonempty list of `Name-Value` pairs holding **exactly** the
  problem's declared output names. `Name` must be an atom: write `'A'-Xs` with
  quotes when the declared name starts with a capital. `Value` is an integer, a
  variable, or a nested list of these, and its shape must match the reference
  exactly.
- Outputs are integers. A Boolean output is `0` or `1` — the reference accepts
  those for a Boolean, and `true`/`false` would arrive as JSON strings and be
  rejected.

### Optimization

Define `model/4` instead. The fourth argument is `min(Expr)`, `max(Expr)` or
`none`, and `Expr` is an arithmetic expression over the model's variables:

```prolog
% model(+Instance, -Vars, -Outputs, -Objective)
model(Instance, Vars, [x-X, y-Y], min(X + Y)) :-
    N = Instance.n,
    Vars = [X, Y],
    Vars ins 0..N,
    X + Y #>= N.
```

The driver proves the optimum with `labeling/2`'s `min`/`max` option, then fixes
it and enumerates only assignments that achieve it. Do not add your own
objective bound: a model that hardcodes the optimum it expects is wrong even
when it passes.

### Choosing the search

The default labelling options are `[ff]`. A submission may choose its own by
defining `labeling_options/1`, which the driver reads once:

```prolog
labeling_options([ffc, bisect]).
```

`min/1` and `max/1` are refused there — the objective belongs to `model/4`.

## What makes a submission fail

- **Do not solve.** `label/1`, `labeling/2`, `findall/3` over solutions,
  `format/2`, `write/1` and `halt/0` all belong to the driver. Anything printed
  on standard output corrupts the protocol.
- **Take every quantity from `Instance`.** A model that hardcodes the numbers of
  the example is the one failure this benchmark exists to catch, and it is
  rejected the moment a second instance is checked.
- **Give every variable a finite domain** with `ins`/`in` before it is
  constrained. Labelling an unbounded variable raises
  `Arguments are not sufficiently instantiated`, which the runner reports as an
  error rather than a solution.
- **`model/3` failing means "no solution".** A typo that makes the clause fail
  is reported as `unsat`, and an unsatisfiable submission never passes. If a
  model is rejected as `no_solution`, suspect a failing goal (a wrong arity, an
  unbound arithmetic `is`, a list length that does not match) before suspecting
  the constraints.
- **`=` is not `#=`.** `X = Y` unifies terms; `X #= Y` is the arithmetic
  constraint. `is/2` evaluates only ground arithmetic and throws on a
  constrained variable.
- **`findall/3` copies its template, so it cannot collect decision variables.**
  Constraints posted on what it returned hold over copies and never reach the
  model, which the evaluator reports as `invalid_solution` — a solution that
  ignores a constraint you can see in the source. Use `findall/3` for ground
  data such as index pairs, and build lists of variables by mapping or
  recursion, which unify rather than copy.
- **A lambda shares only the variables named in its `{...}` set.** `library(yall)`
  expands a lambda at compile time, so a variable from the surrounding clause
  that is not declared is local to the lambda however bound it is at call time.
  `maplist({Cells}/[Row]>>(length(Row, N), Row ins 1..Cells), Rows)` with `N`
  left out silently labels rows of every length instead of length `N`.
- **`maplist/5` is the widest there is** — a goal and four lists. A model that
  needs to walk more lists in step maps over the indices and reads each list
  with `nth1/3`.

## The API, verified against SWI-Prolog 9.2.9

### Arithmetic and reification

| Form | Meaning |
| --- | --- |
| `#=` `#\=` `#<` `#=<` `#>` `#>=` | arithmetic relations over expressions |
| `X in 1..9`, `Xs ins 1..9` | domain of one variable / of a list |
| `X in 1..3 \/ 7..9` | a domain with a hole |
| `+ - * // div mod rem abs min max ^` | expression operators, all integer |
| `#\/ #/\ #\ #==> #<== #<==> #\+` | disjunction, conjunction, exclusive or, implication, equivalence, negation of *constraints* |

`B #<==> (X #= V)` reifies a constraint into a 0/1 variable, which is how you
count things:

```prolog
occurrences(Value, Xs, Count) :-
    maplist({Value}/[X, B]>>(X #= Value #<==> B), Xs, Bs),
    sum(Bs, #=, Count).
```

### Global constraints

| Constraint | Meaning |
| --- | --- |
| `all_different(Xs)` | pairwise distinct, weaker propagation |
| `all_distinct(Xs)` | pairwise distinct, domain-consistent; prefer it |
| `sum(Xs, #=, Expr)` | the sum of `Xs` stands in that relation to `Expr` |
| `scalar_product(Cs, Xs, #=, Expr)` | the weighted sum |
| `element(I, Xs, V)` | `V` is the `I`-th element of `Xs`, **1-based**, `I` may be a variable |
| `global_cardinality(Xs, [K-N, ...])` | value `K` occurs `N` times; `N` may be a variable |
| `circuit(Succs)` | the successor list forms one Hamiltonian circuit |
| `tuples_in(Tuples, Relation)` | each tuple is a row of the ground relation |
| `lex_chain(Lists)` | the lists are lexicographically non-decreasing |
| `chain(Xs, #=<)` | consecutive elements stand in that relation |
| `serialized(Starts, Durations)` | tasks do not overlap in time |
| `disjoint2(Rectangles)` | `f(X, W, Y, H)` rectangles do not overlap |
| `cumulative(Tasks, [limit(L)])` | resource limit over `task(S, D, E, C, Id)` |
| `automaton(Xs, Nodes, Arcs)` | the sequence is accepted by an automaton |
| `transpose(Rows, Columns)` | transpose a list of lists |

There is **no** `nvalue/2` and no `count/4`: reify and sum, or use
`global_cardinality/2`.

### Labelling options the driver accepts

Variable choice `leftmost` (default), `ff`, `ffc`, `min`, `max`; value choice
`up` (default), `down`; branching `step` (default), `enum`, `bisect`. One option
per category.

## Idioms that come up in this benchmark

```prolog
% A matrix of variables, and its rows and columns all-distinct.
matrix(N, M, Rows) :-
    length(Rows, N),
    maplist({M}/[Row]>>(length(Row, M), Row ins 1..M), Rows).

latin_square(Rows) :-
    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns).

% Index a matrix with decision variables: flatten it and use element/3, which
% is 1-based. nth0/nth1 only work with an integer index.
cell(Rows, Width, I, J, V) :-
    append(Rows, Flat),
    Position #= (I - 1) * Width + J,
    element(Position, Flat, V).

% Pairwise constraints over a list.
pairs([]).
pairs([X|Xs]) :- maplist(different(X), Xs), pairs(Xs).
different(X, Y) :- X #\= Y.
```

`numlist/3` builds a range, `sum_list/2` sums integers, `nth1/3` and `nth0/3`
index a list with an integer, `msort/2` sorts without removing duplicates, and
`findall/3` is fine for building *data* — just never for collecting solutions.

## Check your own model before submitting

```sh
python -m evaluation.check MODEL.pl --problem PROBLEM --solver swipl_clpfd --instance-count 99
```

`--instance-count 99` checks every instance the problem has, which is what
catches a model that fitted the example.

Read `reason` and `detail` on failure: `invalid_solution` means the reference
rejects a solution your model allows, `suboptimal_solution` means your objective
is wrong, `no_solution` usually means a goal in your clause failed, and
`execution_error` carries the Prolog exception in its detail. `execution_timeout`
means CLP(FD) could not finish in the budget — reach for a stronger propagator
(`all_distinct` over `all_different`), an implied constraint, or a different
labelling strategy through `labeling_options/1`.

Never change the reference, the dataset, or the evaluator to make a submission
pass.
