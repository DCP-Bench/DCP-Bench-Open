# Essence' language reference (Savile Row 1.11.1)

Checked against the Savile Row manual (section numbers in [sources.md](../sources.md)); constructs marked (run) were also executed in the image.

## Declarations

- `given n : int`, `given d : int(0..n)`, `given b : bool`, `given m : matrix indexed by [int(1..n), int(1..n)] of int(0..9)`. A `where` clause constrains parameters and may not mention decision variables.
- `letting c = 10`, `letting d = c*n`, `letting IDX be domain int(1..n)`, `letting T = [ [a,b] | a : int(1..3), b : int(1..3), a < b ]` (comprehension). Define before use. Values are ints, bools or matrices, never decision expressions.
- `find x, y : int(1..10)`, `find s : bool`, `find M : matrix indexed by [int(1..n), IDX] of int(0..1)`. Decision domains must be finite.
- Domains: `int(1..3, 5, 7..20)`, `bool`, `intersect`, `union`, `-`. Reserved words: forall, forAll, exists, sum, such, that, letting, given, where, find, language, int, bool, union, intersect, in, false, true. Identifiers: letter, then letters, digits, `.`.

## Expressions

- Int: `+ - * ** / %`, unary `-`, `abs(x)` or `|x|` (run), `min(a,b)`, `max(a,b)`, `factorial(x)` (0..20), `popcount(x)`. Floor division.
- Comparison `= != < <= > >=`. Boolean `/\ \/ -> <-> !`. A comma between constraints is a conjunction of lowest precedence.
- Set membership: `x in int(1,3,5)`, `x in toSet(M)`; the set must not contain decision variables.
- `toInt(b)` exists but booleans already coerce to int in arithmetic.
- Matrix lexicographic order: `A <=lex B`, `<lex`, `>lex`, `>=lex`, on 1-D matrices.
- Index `M[i,j]`, decision indices allowed (run); slices `M[i,..]`, `M[..,j]`. Literals: `[1,2,3]` is indexed `int(1..3)`; `[1,2,3 ; int(0..2)]` gives another index domain; nested literals make 2-D.
- Comprehension: `[ e | i : D, j : D2, cond ]` with an optional `; index-domain` at the end.
- Matrix functions: `sum(X)`, `product(X)`, `min(X)`, `max(X)`, `flatten(X)`, `flatten(n, X)`, `cat(A,B)`, `toSet(X)`.
- Quantifiers: `forAll i,j : int(1..n) . E`, `exists i : D . E`, `sum i : D . E`, dependent domains `forAll j : int(i+1..n)`. No filter clause: write `forAll i : D . cond -> E`. A matrix domain may be quantified: `forAll p : matrix indexed by [int(1..3)] of int(1..3) . allDiff(p) -> E`.
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

- `minimising E` / `maximising E` (one, int or bool expression), before `such that`.
- `branching on [x, M, [M[i,i] | i : int(1..n)]]`; `heuristic static|sdf|conflict|srf` is Minion only.

## Semantics worth knowing

- Undefined expressions (index out of range, `x/0`) make the enclosing constraint false.
- `%` follows floor division: `a - b*floor(a/b)`.
- `-2**2**3 = -256`: unary minus binds looser than `**`, which is right associative.
- Compile time grows with grid and quantifier size; Savile Row reads the whole model before search, so large instances can time out before Minion starts.
