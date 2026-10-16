# Fewest coins (minimise, command line)

**Problem:** Pay 63 cents with coins of 1, 5, 10 and 25 cents, using as few coins as possible.
**Shows:** `minimize(T, S, term="coins()")` in a `procedure main`, which prints one optimal model; a finite `Count` type for the decisions while the objective stays `-> Int`; a parenthesised product inside `sum{{ }}`.
**Run:** `idp-engine --no-timing coins.idp`
**Expected:** `coins := 6.`
**Expected:** `used := {0 -> 3, 1 -> 0, 2 -> 1, 3 -> 2}.`
