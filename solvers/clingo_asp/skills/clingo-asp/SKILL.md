---
name: clingo-asp
description: Write instance-agnostic Answer Set Programming models for the DCP-Bench clingo_asp integration, covering how the JSON instance arrives as facts, how declared outputs are returned with #show, and the mistakes that make a submission fail.
---

# ASP models for `clingo_asp`

A submission is one clingo program, `model.lp`. The runner grounds and solves it
inside a container; you never call the solver or print anything.

Image: clingo 5.8.2 on Python 3.12. The program is pure ASP — **`#script(python)`
is not available in this build** and raises "python support not available".

ASP does not take an object you read fields off, so this integration differs
from the Python ones in both directions: the instance arrives as **facts**, and
the declared outputs leave as **shown atoms**.

## The instance arrives as facts

The runner converts the JSON instance into ground facts and grounds them with
your program. The rule is always the same — **index positions first, value
last**:

| Instance field | Facts your program sees |
| --- | --- |
| `"n": 12` | `n(12).` |
| `"demand": [250, 255]` | `demand(0,250).` `demand(1,255).` |
| `"rules": [[3,1],[2]]` | `rules(0,0,3).` `rules(0,1,1).` `rules(1,0,2).` |
| `"name": "castle"` | `name("castle").` |
| `"flag": true` | `flag(true).` |

Indices are 0-based. Nested lists add one index position per level. An empty
list produces no facts at all, so write rules that tolerate the predicate being
absent rather than assuming at least one fact.

A field whose name starts with a capital — several problems use `N` — is lowered
to `n`, because ASP reads a leading capital as a variable. Two fields that would
collide after lowering are refused rather than merged.

## The outputs leave as shown atoms

**`#show` is the contract.** Show one predicate per output key in the
reference's `solution = {...}` dictionary, named the same, and show nothing
else. The runner receives the declared keys and matches each to the predicate
with its first character lowered, so a key like `A` is carried by `a` — an ASP
predicate cannot start with a capital. The same
index-then-value shape applies:

| Declared output | What to show |
| --- | --- |
| `"length": 17` | `#show length/1.` giving `length(17)` |
| `"A": [1,4]` | `#show a/2.` — a key starting with a capital is carried by the lowered predicate |
| `"queens": [3,1,4]` | `#show queens/2.` giving `queens(0,3). queens(1,1). queens(2,4).` |
| `"matrix": [[1,0],[0,1]]` | `#show matrix/3.` giving `matrix(0,0,1).` and so on |

Indices must be 0-based and contiguous, or the runner rejects the answer. Values
must be integers or the constants `true`/`false`; a Boolean output may also be
given as `1`/`0`, which the evaluator accepts.

## A complete example

n-queens, whose reference declares `queens` as a list of n integers in 1..n:

```prolog
row(0..N-1) :- n(N).
column(1..N) :- n(N).

% Exactly one column per row.
1 { queens(R,C) : column(C) } 1 :- row(R).

% No shared column or diagonal.
:- queens(R1,C), queens(R2,C), R1 < R2.
:- queens(R1,C1), queens(R2,C2), R1 < R2, R2 - R1 == |C2 - C1|.

#show queens/2.
```

`queens/2` is both the internal predicate and the declared output, which is
usually the tidiest arrangement. When your working predicate does not match the
output shape, derive a separate one and show only that.

## Optimization

Write `#minimize` or `#maximize` as usual. The runner enumerates in `optN` mode
and **only accepts models clingo has proven optimal**; if the budget runs out
before that proof, the result is a timeout rather than a pass. Enumeration of
several solutions then means several distinct *optimal* answers.

```prolog
#minimize { C : cost(C) }.
```

## Gotchas

- **An aggregate cannot be compared to another aggregate.** `:- #sum { ... } !=
  #sum { ... }.` is a parse error, not a semantic one, and the message is only
  "parsing failed". Bind each side first:

  ```prolog
  total(S) :- S = #sum { V : first(V) }.
  other(S) :- S = #sum { V : second(V) }.
  :- total(A), other(B), A != B.
  ```

- **Cardinality bounds go outside the braces**, as `H { p(X) : q(X) } H`, not
  `{ p(X) : q(X) } == H`.
- **Show nothing else.** An extra `#show` becomes an extra declared output and
  the evaluator rejects the submission for having the wrong keys. Debugging
  atoms must be removed, not left shown.
- **Grounding is where ASP dies.** A rule quantified over several large domains
  can generate millions of instantiations before search even starts, and the
  memory cap will end the run. Constrain domains in the rule body, and prefer
  `#count`/`#sum` aggregates to enumerating combinations by hand.
- **Absent predicates are not errors.** If an instance field is an empty list
  the predicate simply has no facts, and a rule that requires it silently yields
  nothing. Guard with a default where that matters.
- **Integer division is `/` and modulo is `\\`** in clingo, and `|X|` is absolute
  value. There is no floating point; the declared outputs must be integers.
- **The reference's commented-out symmetry breaking is not part of the
  contract.** Adding it would exclude valid answers.

## Check your own model before submitting

```sh
python -m evaluation.check MODEL.lp --problem PROBLEM --solver clingo_asp --instance-count 99
```

`--instance-count 99` checks every instance the problem has, which is what
catches a model that fitted the example. Add `-W ignore::SyntaxWarning` to
quieten LaTeX in reference docstrings.

Read `reason` and `detail` on failure: `invalid_solution` means the reference
rejects an answer your program allows, `suboptimal_solution` means your
objective is wrong, `invalid_output` means the shown atoms have the wrong keys,
arities or index ranges, and `execution_timeout` usually means grounding blew up.

Repair the model from the reported reason. Never change the reference, the
dataset, or the evaluator to make a submission pass.
