# Essence' language reference (Savile Row 1.11.1)

Checked against the Savile Row manual (section numbers in [sources.md](../sources.md)); constructs marked (run) were also executed with Savile Row 1.11.1.

## Declarations

- `given n : int`, `given d : int(0..n)`, `given b : bool`, `given m : matrix indexed by [int(1..n), int(1..n)] of int(0..9)`. A `where` clause constrains parameters and may not mention decision variables.
- `letting c = 10`, `letting d = c*n`, `letting IDX be domain int(1..n)`, `letting T = [ [a,b] | a : int(1..3), b : int(1..3), a < b ]` (comprehension). Define before use. Values are ints, bools or matrices, never decision expressions.
- `find x, y : int(1..10)`, `find s : bool`, `find M : matrix indexed by [int(1..n), IDX] of int(0..1)`. Decision domains must be finite.
- Domains: `int(1..3, 5, 7..20)`, `bool`, `intersect`, `union`, `-`. A bound may be a sum over a given 1-D matrix, `int(0..sum(v))` or `int(0..sum i : int(1..n) . npv[i])` (both run). A restriction by `in` in a find domain does not parse (`find p : int(2..10000) in int(2,3,5)` fails); list the values instead: `find p : int(2,3,5,7)` (run).
- Reserved words: forall, forAll, exists, sum, such, that, letting, given, where, find, language, int, bool, matrix, union, intersect, in, false, true. Also rejected as a `find` name (run): `min`, `max` and `table` (`ERROR: Parsed keyword 'max'`); the keyword words fail with `ERROR: Parsed 'find' keyword.`. Accepted as names (run): `E`, `abs`, `element`, `allDiff`, `flatten`, `toInt`, `on`, `of`, `by`, `be`, `domain`, `heuristic`, `branching`, `indexed`, `minimising`, but avoid them for readability. Rename a clashing name with a suffix (`max_`, `where_`). Identifiers: letters, digits and `_` (`MAX_STEPS`, `my_var_2` run); a `.` does not parse.

## Expressions

- Int: `+ - * ** / %`, unary `-`, absolute value `|x|` (run; `abs(x)` fails to parse), `min(a,b)`, `max(a,b)`, `factorial(x)` (0..20), `popcount(x)`. Floor division. `%` on a decision variable works: `x % 2 = 1` (run).
- Comparison `= != < <= > >=`. Boolean `/\ \/ -> <-> !`. A comma between constraints is a conjunction of lowest precedence.
- Set membership: `x in int(1,3,5)`, `x in toSet(M)`; the set must not contain decision variables. `x in toSet(S)` with `S` a `letting` comprehension runs.
- `toInt(b)` exists but booleans already coerce to int in arithmetic. `toInt(x[i] = true) * i` runs, but weighted sums of it propagate poorly (see SKILL.md, Search).
- Matrix lexicographic order: `A <=lex B`, `<lex`, `>lex`, `>=lex`, on 1-D matrices, and on rows as slices: `M[r,..] <=lex M[r+1,..]` (run).
- Index `M[i,j]`, decision indices allowed (run); slices `M[i,..]`, `M[..,j]`. Literals: `[1,2,3]` is indexed `int(1..3)`; `[1,2,3 ; int(0..2)]` gives another index domain; nested literals make 2-D. A list literal can be indexed directly, with a constant or a decision index: `v = [1,3,8,120][i]` (run, `i = 4` gives 120).
- Comprehension: `[ e | i : D, j : D2, cond ]` with an optional `; index-domain` at the end.
- Matrix functions: `sum(X)`, `product(X)`, `min(X)`, `max(X)`, `flatten(X)`, `flatten(n, X)`, `cat(A,B)`, `toSet(X)`. `sum` and `max` take a 1-D matrix: `sum(M)` on 2-D fails with `Expected one-dimensional matrix in sum function`, so use `sum(flatten(M))` (run).
- Quantifiers: `forAll i,j : int(1..n) . E`, `exists i : D . E`, `sum i : D . E`, dependent domains `forAll j : int(i+1..n)`. Several variables share one domain by grouping: `exists a, b : int(1..3) . E` (run); `exists a : int(1..3), b : int(1..3) . E` does not parse, and neither does `forAll i : int(1..n), j : int(1..m)` with different domains (run). Nest instead: `forAll i : int(1..n) . forAll j : int(1..m) . E` (run). No filter clause: write `forAll i : D . cond -> E`. A matrix domain may be quantified: `forAll p : matrix indexed by [int(1..3)] of int(1..3) . allDiff(p) -> E`.
- Always parenthesise a quantified sum used in a comparison: `(sum i : D . x[i]) <= c`.

## Globals (boolean, nestable)

| call | meaning |
|---|---|
| `allDiff(X)` | X (1-D) pairwise distinct (run) |
| `alldifferent_except(X, v)` | distinct except value v may repeat |
| `gcc(X, Vals, Counts)` | Vals[i] occurs exactly Counts[i] times (run) |
| `atleast(X, Counts, Vals)`, `atmost(X, Counts, Vals)` | at least / at most Counts[i] copies of Vals[i] (counts before values) |
| `table(X, T)` | row of X is a row of T (T has no decision variables) (run) |
| `cumulative(Starts, Durs, Res, Bound)` | resource limit over time |

For forbidden tuples build the complement of the table with a comprehension.

## Solve section

- `minimising E` / `maximising E` (one, int or bool expression), after `branching on` and before `such that`. Verified: `minimising` placed before `branching on` is a parse error.
- `branching on [x, M, [M[i,i] | i : int(1..n)]]`. A comprehension is one entry of the list: `branching on [[x[i] | i : int(1..n), i > 1]]` (conditional) and `[[a[n+1-i] | i : int(1..n)]]` (arithmetic index) both run. The bare `branching on [e | i : D]` and `branching on [[x[i], y[i]] | i : D]` fail with `Parsed entry in list`. `branching on [a[1], a[2]]` runs.
- `heuristic static|sdf|conflict|srf` is Minion only. It goes before `such that`, on either side of `branching on` (run); after `such that` it is read as a constraint and fails.
- `cumulative(s, [2,2,2], [1,1,1], 1)` runs with `s` a 1-D matrix of starts.

## Semantics worth knowing

- Undefined expressions (index out of range, `x/0`) make the enclosing constraint false.
- `%` follows floor division: `a - b*floor(a/b)`.
- `-2**2**3 = -256`: unary minus binds looser than `**`, which is right associative.
- Compile time grows with grid and quantifier size; Savile Row reads the whole model before search, so large instances can time out before Minion starts.
