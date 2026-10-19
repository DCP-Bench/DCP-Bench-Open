# Shift cover (table, element, lex, minimise)

**Problem:** 4 workers, one shift each (0, 1 or 2). Consecutive workers must take an allowed pair of shifts. Cost depends on worker and shift. Workers 0 and 1 are interchangeable, so their shifts are ordered lexicographically. Minimise total cost.
**Shows:** table constraint as an `Or` over allowed pairs, element lookup by an `If` chain, lexicographic order by a recursive helper, minimisation by tightening.
**Run:** `python model.py`
**Expected:** `Optimal cost: 8`
