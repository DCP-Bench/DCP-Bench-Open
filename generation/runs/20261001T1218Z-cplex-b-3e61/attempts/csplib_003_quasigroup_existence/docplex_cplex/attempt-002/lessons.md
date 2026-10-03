# Lesson: quadratic constraints count against the Community Edition limit

This attempt posts 243 linear Latin-square constraints, 81 + 324 linear implied constraints and
729 quadratic `<=` constraints over binary products (with `optimalitytarget = 3`). On m = 9 the
runner reported `unsupported_capability`: "Problem size limits (1000 vars, 1000 consts)
exceeded, model has 729 vars, 1377 consts, CPLEX code=1016". 1377 = 243 + 81 + 324 + 729, so
each quadratic constraint counts as one constraint. Attempt 001 (243 linear + 729 quadratic =
972) was within the limit and was not refused.

`preprocessing.qtolin = 1` (attempt 004, and session1_magic_square attempt 003) was accepted by
the Community Edition and gave no size refusal.
