---
name: picat
description: Write instance-agnostic Picat models for the DCP-Bench picat integration, covering the model/4 submission contract, the cp and sat solver modules of Picat 3.9#12, how instance data and outputs are represented, and the language traps (eager function calls, indexing by a decision variable) that make a submission fail.
---

# Picat models for `picat`

Write one Picat file that *states* a model. A driver inside the container
compiles it, calls `model/4`, runs the search, proves the optimum when there is
an objective, enumerates distinct solutions and writes them out. You never call
`solve/1`, `solve/2`, `println/1` or anything that searches or prints for the
answer yourself.

Image: the official Picat 3.9#12 64-bit Linux build. The `cp` and `sat` solver
modules are there, and so are the library modules `util`, `ordset`, `os`,
`math` and `datetime`. `mip` and `smt` are not usable: they call an external
MIP or SMT solver and none is installed. There is no network.

## The contract

```picat
import cp.

model(Data, Vars, Outputs, Options) =>
    N = Data.get(n),
    [X, Y] :: 0..N,
    X + Y #= N,
    Vars = [X, Y],
    Outputs = [x = X, y = Y],
    Options = [].
```

- **Import exactly one of `cp` and `sat`.** The driver solves with whichever
  one the file imports and refuses a file that imports neither, both, `mip` or
  `smt`. Importing other library modules (`import util.`) is fine.
- **`Data`** is the instance as a Picat map. Read a field with
  `Data.get(key)`. Keys are atoms, so a field whose name starts with a capital
  or an underscore is read with a quoted atom: `Data.get('NUM_CELLS')`,
  `Data.get('_SHIP')`. `Data.key` does **not** work on this map.
  - JSON arrays arrive as lists, nested arrays as lists of lists. Index them
    1-based: `Grid[2, 1]` is row 2, column 1 of a list of lists.
  - JSON strings arrive as Picat strings (lists of one-character atoms).
  - JSON `true`/`false` arrive as `1`/`0`; a JSON object arrives as a map.
- **`Vars`** is the decision variables to label, as a list, an array, or nested
  lists or arrays of them. Put every decision variable in it, including
  auxiliary ones. The driver adds any variable still free in `Outputs` or in
  the objective, and with `cp` it finally labels whatever is left in suspended
  constraints, but the order it labels in is `Vars` first, so `Vars` is where
  the search happens.
- **`Outputs`** is a nonempty list of `Name = Value` pairs holding **exactly**
  the problem's declared output names (a map works too). `Name` is an atom —
  `'A' = Xs` with quotes when the declared name starts with a capital — or a
  string. `Value` is an integer, a domain variable, a string, or a list or
  array of these, nested to the declared shape. A two-dimensional array from
  `new_array(R, C)` comes out as a list of rows.
- **Booleans are `0`/`1`.** A declared Boolean output is an integer variable
  over `0..1`; the reference accepts `0` and `1`.
- **`Options`** is the list passed to `solve/2`: search options such as `ff`
  for `cp`, and at most one objective, `$min(Obj)` or `$max(Obj)`. Write the
  `$`: it is what makes `min(Obj)` a term rather than a call to the `min`
  function. `Obj` may be a variable or an expression over the model's variables.

### Optimisation

```picat
import cp.

model(Data, Vars, Outputs, Options) =>
    Durations = Data.get(durations),
    N = len(Durations),
    Starts = new_list(N),
    Starts :: 0..sum(Durations),
    serialized(Starts, Durations),
    Makespan :: 0..sum(Durations),
    foreach (I in 1..N)
        Starts[I] + Durations[I] #=< Makespan
    end,
    Vars = Starts,
    Outputs = [starts = Starts, makespan = Makespan],
    Options = [$min(Makespan)].
```

The driver first solves with the objective until the optimum is **proven**,
then builds the model again with the objective fixed at that value and
enumerates distinct declared outputs. A run that ends before the proof reports
a timeout, never a solution. Do not bound the objective yourself to "help", and
never put a known optimum into the model.

## Instance data, worked through

```picat
model(Data, Vars, Outputs, Options) =>
    Costs = Data.get(cost_matrix),          % list of lists
    NStores = len(Costs),
    NWarehouses = len(Costs[1]),
    Capacity = Data.get(capacity),          % list
    Names = Data.get(warehouse_names),      % list of strings
    ...
```

Bind a field to a variable before indexing it: `Data.get(xs)[1]` is a syntax
error, `Xs = Data.get(xs), Xs[1]` is not. Convert a list to an array with
`to_array(L)` when a model indexes it heavily; both are 1-based.

## Constraints

Every row below was run in this image, with `cp` and with `sat`.

| Constraint | Picat |
| --- | --- |
| domain | `X :: 1..N`, `Xs :: 0..9`, `X :: [1, 3, 5]`, `X notin [2, 4]` |
| arithmetic | `#=`, `#!=`, `#<`, `#=<`, `#>`, `#>=` over `+ - * // div mod abs`, and `sum`, `prod`, `max` of a list |
| logic | `#~ C`, `C1 #/\ C2`, `C1 #\/ C2`, `C1 #^ C2`, `C1 #=> C2`, `C1 #<=> C2`; a constraint inside an expression counts 1 when it holds |
| counting | `sum([X[I] #= V : I in 1..N]) #= K`, `count(V, Xs) #>= 1`, `count(V, Xs, #=, K)`, `global_cardinality(Xs, [$(1-C1), $(2-C2)])`, `nvalue(K, Xs)` |
| all different | `all_different(Xs)`, `all_distinct(Xs)` (stronger propagation in `cp`), `all_different_except_0(Xs)` |
| lookup | `element(I, List, V)` (1-based), `element0(I, List, V)`, `matrix_element(M, I, J, V)` (M a list of lists or a two-dimensional array) |
| tables | `table_in({X, Y}, [{1, 2}, {2, 3}])`, `table_notin(...)`; the guide also allows a list of variable tuples against one table |
| sequences | `regular(Xs, Q, S, M, Q0, F)`, `increasing(Xs)`, `increasing_strict`, `decreasing`, `lex_le(Xs, Ys)`, `lex_lt` |
| graphs | `circuit(Xs)`, `subcircuit(Xs)` |
| scheduling | `cumulative(Starts, Durations, Resources, Limit)`, `serialized(Starts, Durations)`, `diffn(Rects)` |
| conditional value | `V #= cond(C, Then, Else)` |

`sum`, `max` and `prod` take a list, which a list comprehension written inside
the constraint builds: `sum([Weights[I] * X[I] : I in 1..N]) #=< Capacity`
(see trap 1 for why it has to be inside), with filters after the iterators:
`sum([E : Row in M, E in Row, E > 2])`. `util` adds `transpose/1` for lists of
lists.

## Traps

Picat evaluates a function call wherever one appears in an argument, which is
where most failed submissions go wrong. These were each reproduced:

1. **Arithmetic outside a constraint is computed immediately.** Inside `#=`,
   `#<` and the other constraint operators an expression is a term, so
   `X + Y #= N` is fine. Anywhere else — a list element, an output value, the
   argument of a global constraint — `X + Y` is evaluated at once and fails with
   `instantiation_error` while `X` is still a variable. Give the value a name
   with a constraint: `S #= X + Y`, then use `S`.
   List comprehensions follow the same line. Written directly inside a
   constraint or an objective, `sum([W[I] * X[I] : I in 1..N]) #= S` and
   `$max(sum([W[I] * X[I] : I in 1..N]))` keep their arithmetic. Bound to a
   variable first (`L = [W[I] * X[I] : I in 1..N]`) or passed to a global
   constraint (`all_different([Q[I] - I : I in 1..N])`), every element is
   computed at once and fails. For a global constraint over expressions, name
   them first:
   `D = new_list(N), foreach (I in 1..N) D[I] #= Q[I] - I end, all_different(D)`.
2. **A term that shares a name with a function needs `$`.** `$min(Cost)`,
   `$max(Profit)`, and the key-count pairs of `global_cardinality`,
   `[$(1-C1), $(2-C2)]`, are written with `$`, or Picat calls `min/1` or
   subtracts.
3. **No indexing by a decision variable.** `L[I]` with `I` a domain variable
   raises `type_error(integer, ...)`. Use `element(I, L, V)`, `element0/3` or
   `matrix_element/4`.
4. **Variables are single-assignment.** `X = X + 1` fails. Accumulate in a loop
   with `:=` (`Total := Total + X[I]`), or better, with `sum/1`.
5. **Loops scope their variables.** A variable that first appears inside a
   `foreach` body is new in each iteration, which is what lets a loop body name
   a temporary. A variable the loop has to bind for later use must appear
   before the loop.
6. **`if ... then ... else ... end` needs its `end`**, and `==` tests while `=`
   unifies. Use `if` for instance-dependent structure, never to test a decision
   variable: posting a constraint (`#=>`, `#<=>`) is how a condition on a
   variable is stated.
7. **Rules match; they do not unify.** A `=>` rule selects on its head by
   one-way matching, so write helper predicates with variable heads or
   explicit tests, and bind outputs in the body as `model/4` above does.
8. **Output variables need domains.** An output that no constraint and no `::`
   ever touched is not a domain variable, and the solver stops with
   `dvar_expected` or `free_var_not_allowed`.
9. **Only arithmetic and logical constraints can be combined.** `#\/`, `#=>`,
   `#<=>` and the rest take constraints built from `#=`, `#<` and the like.
   A global constraint inside one (`increasing_strict(Xs) #\/ B #= 1`) raises
   `invalid_constraint_exp`; state the condition with arithmetic instead.

## Choosing `cp` or `sat`

Both modules take the same constraints, and a model that works with one runs
unchanged with the other. `cp` propagates and searches, and its search options
(`ff`, `ffc`, `split`, `down`, `rand` and others, listed in the Picat guide)
decide how it searches. `sat` compiles the whole model into clauses and hands
them to a SAT solver; it accepts the `cp` options without complaint, but the
guide gives them no meaning there. Neither is faster in general. When an
attempt times out, trying the other import is a legitimate repair; say in the
reasoning which one you chose and why.

## What the runner reports

- A syntax error comes back as `error(syntax_error,picat)` followed by
  Picat's own message with the line range, for example
  `*** SYNTAX ERROR *** (4-6) wrong list format.`
- A `model/4` that fails (a constraint posted on constants that do not hold it,
  a failed test) is `unsat`, and the evaluator reports `no_solution`.
- An exception is an error with the thrown term as detail, for example
  `existence_error(procedure, ... model / 4)` when the predicate is misnamed.
- `println/1` inside a model goes to the log, not to the answer. It never
  helps and should not be left in.

## Reasoning to record

Say which module you imported and why, where each domain bound comes from in
the instance, and which search options you chose. If an attempt timed out, say
what you changed: the module, the options, a redundant constraint, or a tighter
domain.
