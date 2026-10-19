---
name: picat
description: Picat, a logic-based language whose constraint modules cp and sat solve finite-domain and SAT-encoded problems. Use when writing, debugging or explaining Picat models with cp or sat, or when a user has chosen Picat for a constraint or optimisation problem.
license: Apache-2.0
compatibility: Requires Picat 3.9#12 (free for any use; C sources under MPL 2.0) and a Linux, macOS or Windows host. The mip and smt modules need external solvers and are not covered.
metadata:
  domain: constraint-programming
  solver: picat
  paradigm: cp
---

# Picat (cp and sat)

Picat is a rule-based language with a constraint library. A model states variables, domains and constraints; `solve` searches for values. Constraint operators such as `#=` and `::` post constraints at once, while an arithmetic expression outside a constraint is computed at once. Keep that split in mind and most errors are avoided.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Writing Picat correctly](#writing-picat-correctly)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/`, one folder per pattern, including `assets/read-json-instance/` for reading JSON

## Install

```bash
curl -LO https://picat-lang.org/download/picat39_12_linux64.tar.gz
echo "f053b11cccabfb69a3ccd779f2dc1c24cdf889805799bc8c779e6c56da703e4a  picat39_12_linux64.tar.gz" | sha256sum -c
tar -xzf picat39_12_linux64.tar.gz
export PATH="$PWD/Picat:$PATH"
picat --version        # Picat version 3.9#12
```

The archive unpacks to `Picat/`, which holds the `picat` executable and the library modules `cp`, `sat`, `util`, `ordset`, `math` and others. Archives for other platforms are on the [download page](https://picat-lang.org/download.html). Details: [Picat download](https://picat-lang.org/download.html), [Picat guide, install chapter](https://picat-lang.org/download/picat_guide_html/picat_guide.html).

If Picat was unpacked somewhere not on `PATH` (a container image, say), a bare `picat` fails with `picat: not found` (exit 127): call the executable by its full path, or add its directory to `PATH`.

## Quick start

```picat
import cp.

main =>
    X :: 1..10,
    Y :: 1..10,
    X + Y #= 12,
    X #< Y,
    if solve([X, Y]) then
        println([X, Y])
    else
        println(unsat)
    end.
```

Run with `picat quickstart.pi`. It prints `[2,10]`. Every program needs a `main/0` or `main/1`; `picat file.pi` calls it. With `main(Args)`, `picat file.pi instance.json` passes the arguments as a list of strings, so `Args[1]` is the file name as a list of characters.

## Modelling

Full list of constraints: [Picat guide, constraints chapter](https://picat-lang.org/download/picat_guide_html/picat_guide.html).

| Need | Picat |
|---|---|
| integer variable with domain | [`X :: 1..N`](https://picat-lang.org/download/picat_guide_html/picat_guide.html), `X :: [1,3,5]`, `X notin [2,4]` |
| list of variables | `new_list(N)`, then `Xs :: 0..9`; two-dimensional: `new_array(R, C)` |
| all different | [`all_different/1`](https://picat-lang.org/download/picat_guide_html/picat_guide.html) (`all_distinct/1` propagates more in `cp`) |
| element lookup (1-based) | [`element/3`](https://picat-lang.org/download/picat_guide_html/picat_guide.html), `element0/3`, `matrix_element/4` |
| table | `table_in/2`, `table_notin/2` |
| counting | `count/4`, `global_cardinality/2`, `nvalue/2` |
| cumulative / no-overlap | `cumulative/4`, `serialized/2`, `diffn/1` |
| circuit | `circuit/1`, `subcircuit/1` |
| sequences | `regular/6`, `increasing/1`, `decreasing/1`, `lex_le/2` |
| reification / implication | `#<=>`, `#=>`, `#\/`, `#/\`, `#~` |
| conditional value | `V #= cond(C, Then, Else)` |
| minimise / maximise | `$min(Expr)` / `$max(Expr)` as an option, see [Solving](#solving) |

Write `$min` and `$max` with the `$`: without it, `min(...)` is a call to the function `min` and nothing is optimised. Arithmetic inside a constraint stays a term, so `X + Y #= N` is fine; outside one it is computed at once (see [Common issues](#common-issues)).

Operators to get right: `**` is power (`10**2` is `100`) and works inside a `cp` constraint (`Z #= 2 ** X`); `^` is bitwise XOR (`10^2` is `8`), and inside a constraint it raises `invalid_constraint_expression`. See [Writing Picat correctly](#writing-picat-correctly).

Each constraint row above is the library's name; the full reference is in the [guide](https://picat-lang.org/download/picat_guide_html/picat_guide.html).

## Solving

Official: [solving options](https://picat-lang.org/download/picat_guide_html/picat_guide.html) (common options, `cp` options, `sat` options).

| Call | Meaning |
|---|---|
| `solve(Vars)` | first solution, labelling `Vars` |
| `solve(Options, Vars)` | the same with options; **Options come first** |
| `solve([$min(Obj)], Vars)` | optimise; the solution returned is optimal |
| `solve([$max(Obj)], Vars)` | optimise, maximising |
| `solve_all(Vars)` / `findall(Vars, solve(Vars))` | every solution, see [All solutions](#all-solutions) |

| Outcome | How it shows |
|---|---|
| Solution found | `solve` succeeds; variables are bound |
| Infeasible | `solve` fails, or posting a constraint fails. Test with `if ... then ... else ... end` |
| Optimum | `solve` with `$min`/`$max` gives the optimal values; Picat searches until the value is proven |
| Time limit | `time_out(solve(Vars), Millis, Res)`: `Res` is `success` or `time_out` ([sys module](https://picat-lang.org/modules.html)) |

Read values by printing the bound variables (`println(X)`). An unbound variable prints as a name like `_123`, which means a missing domain or label. Options for `cp` include `ff`, `ffc`, `down`, `split`, `rand`; `sat` accepts them without effect. Full lists: [solving options](https://picat-lang.org/download/picat_guide_html/picat_guide.html).

**Choosing `cp` or `sat`.** Both modules take the same constraints, so switching is the `import` line. `cp` propagates and searches; `sat` compiles the model to clauses for a SAT solver. Neither is faster in general. When one times out, the other is a fair try.

**Where errors appear.** Syntax errors go to stderr as `*** SYNTAX ERROR *** (line-range) message` with exit code 1. Runtime errors go to stderr as `*** error(...)`. Undefined predicates go to stderr as `*** Undefined procedure`. `println` writes to stdout.

## All solutions

`findall(Vars, solve(Vars))` returns every solution of `Vars`. `solve_all(Vars)` is the same. Enumerate only the decision variables: an auxiliary variable that differs makes two solutions look distinct. Details: [guide, findall and solve](https://picat-lang.org/download/picat_guide_html/picat_guide.html).

**All optimal solutions.** Solve once with the objective to prove the optimum, rebuild the model (bindings from the first solve cannot be undone), post `Obj #= Optimum`, then enumerate. A builder predicate keeps the two copies identical. See `assets/all-optimal-vertex-covers/`.

## Writing Picat correctly

These rules are where most failed attempts went wrong. Each one fails silently or with a message that does not point at the cause.

**Clause kinds.** `Head => Body` matches its head: an argument in the head must match the call, it does not unify. So `sk(Cs, Cs) => true.` called as `sk([1], Y)` fails, because `Y` is not matched against `[1]`. Output arguments must be bound in the body (`Out = ...`), and a predicate with output arguments is written with `:-`, which unifies its head. Use `=>` for functions and for predicates whose arguments are all inputs; use `:-` for everything that builds an output (a parser, a predicate that returns a list).

```picat
% wrong: pair(1, Y) fails, because the head [X,X] is matched against the unbound Y
pair(X, [X, X]) => true.

% right: the output is bound in the body
pair(X, Out) => Out = [X, X].

% also right: with :- the head unifies, so the output can be in the head
pair(X, [X, X]) :- true.
```

**Operators.** `**` is power, `^` is XOR. `10**2` is `100`, `10^2` is `8`. `**` also works inside a `cp` constraint (`Z #= 2 ** X` with `X :: 0..3`). `^` inside a constraint raises `invalid_constraint_expression`, so use `**`, or compute the value outside the constraint first.

**Indexing.** `L[I]` and `G[R,C]` index lists and arrays, and `G[R,C]` works for a list of lists as well as for `new_array`. Chained `L[1][2]` is a syntax error (`wrong expression`): bind the row first (`Row = L[1], Row[2]`) or use `L[1,2]`.

**Index as a condition.** `if IsLast[T] then` and `if not IsLast[T] then` raise `invalid_subgoal:index_operator`. An index is a value, not a goal. Compare it (`if IsLast[T] == 1 then`) and store flags as 0/1 integers.

**Booleans from comprehensions.** A relational operator outside a constraint or an `if` condition stays an unevaluated term. `[K == N : K in 1..2]` gives `[1 == 4, 2 == 4]`, not booleans, and `if X[T] == true` misbehaves. Compute a flag in an `if` inside a `foreach` or a helper predicate, or make it a 0/1 decision variable with `#<=>`.

**Characters.** A letter is a character literal: `$a` is `a`, and `[$a, $b]` prints `ab`. Quoted digits and punctuation do not compare as characters: `C >= '0'` and `$'5' >= $'0'` fail with `Wrong function in expression`, and a bare `$0` is the integer 0. Compare codes with `ord/1` instead: `ord(C) >= 48, ord(C) =< 57` for digits, `ord(C) == 123` for `{`.

**Reading files and JSON.** Picat 3.9 has no JSON library: `json_decode` and `parse_json` are undefined (`Undefined procedure`). Read the text with `read_file_chars(Path)` and parse it in Picat. `assets/read-json-instance/model.pi` is a working reader for objects, arrays, integers and strings, with a `main(Args)` that reads the file given on the command line; copy it into a model.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `instantiation_error` on an output value, a list element or a global constraint argument such as `[X + 5, Y]` | arithmetic outside a constraint is computed at once while `X` is still unbound | name the value first: `S #= X + Y`, then use `S` |
| `instantiation_error` on `L = [W[I]*X[I] : I in 1..N]` | list comprehension outside a constraint | keep it inside `sum(...) #= S` or `$max(...)`, or build the list with `foreach` and `#=` |
| `type_error(integer, ...)` on `L[I]` | indexing by a decision variable | `element/3`, `element0/3`, `matrix_element/4` |
| Model fails silently, optimum is not optimal | `solve` arguments swapped: `solve([X], [$max(X)])` labels only the options list | `solve([$max(X)], [X])` |
| `X = X + 1` fails | variables are single-assignment | accumulate with `:=` in a loop, or use `sum/1` |
| `dvar_expected` or `free_var_not_allowed` | a variable (often an output) has no domain | give it a domain with `::` and a constraint |
| `invalid_constraint_exp` | a global constraint inside `#\/`, `#=>`, `#<=>` | state the condition with arithmetic |
| Whole program stops with `error(failed, main/0)` | a constraint posting failed (infeasible), outside an `if` | wrap the posting in `if (...) then ... else ... end` |
| `wrong list format` syntax error | a missing `]` or `,` | check the line range printed with the error |
| `sat` returns assignments that break an equality with `all_different` over sums of 0/1 variables | defect in `sat` with `all_different/1` over such variables; `cp` is correct | write the pairwise form `foreach (I in 1..N-1, J in I+1..N) Z[I] #!= Z[J] end`, or use `import cp.` |
| Search takes too long | labelling order or weak propagation | try the other module, add `ff`, tighten domains, add a redundant constraint, or use a global constraint |
| `Undefined procedure` / `existence_error` | misnamed predicate or missing `import` | check the name and the module that defines it |
| `Undefined procedure` for `json_decode` or `parse_json` | Picat 3.9 has no JSON library | read with `read_file_chars` and parse; see `assets/read-json-instance/` |
| `picat: not found`, exit 127 | the `picat` executable is not on `PATH` | call it by its full path, or add its directory to `PATH` (see [Install](#install)) |
| `Undefined procedure: char/1` | Picat has no `char/1` | `chr/1` turns a code into a character (`chr(48)` is `0`); `ord/1` turns a character into its code |
| `predicate_used_as_function` | a predicate written where a value is expected, such as `X = jr(...)` | call it as a goal, `jr(Out)`, and read `Out`; or define it with `=` if it returns a value |
| Program prints nothing for a parsed value, or the call fails | `=>` head with an output argument, matched not unified | bind outputs in the body or use `:-`; see [Writing Picat correctly](#writing-picat-correctly) |
| `10^2` gives `8`, or `^` inside a constraint raises `invalid_constraint_expression` | `^` is XOR, not power | write `**` for power |
| `wrong expression` on `L[1][2]` | chained indexing | `L[1,2]`, or bind `Row = L[1]` first |
| `invalid_subgoal:index_operator` on `if IsLast[T]` | an index used as a goal | compare it: `if IsLast[T] == 1` |
| A comprehension of comparisons prints `1 == 4` terms, and an `if` on it takes the wrong branch | relational operators stay terms outside constraints and `if` conditions | build the flag in an `if` inside a `foreach`, or use a 0/1 variable with `#<=>` |
| `Wrong function in expression: '0'` on `C >= '0'` | a quoted digit is not a character literal | compare `ord(C)` with numbers; `$a` is a letter |

Deeper notes on the traps above: [guide, constraints and solving](https://picat-lang.org/download/picat_guide_html/picat_guide.html).

## Further reading

- Picat guide (HTML): https://picat-lang.org/download/picat_guide_html/picat_guide.html
- Picat guide (PDF): https://picat-lang.org/download/picat_guide.pdf
- Modules and library reference: https://picat-lang.org/modules.html
- Downloads and releases: https://picat-lang.org/download.html
