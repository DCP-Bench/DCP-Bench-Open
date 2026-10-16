# One-machine schedule (scheduling, minimise with a time limit)

**Problem:** Five jobs with durations 3, 2, 4, 1, 2 run on one machine without overlap; job 0 and job 1 precede job 2, which precedes job 4. Minimise the time the last job ends.
**Shows:** a disjunctive no-overlap constraint over pairs `i < j`; precedences as a predicate; a finite `Time` type for start times; driving `theory.optimize_solver` (a `z3.Optimize`) with a timeout, telling infeasible (`unsat`), gave up (`unknown`), unbounded (infinite bounds) and proven optimal (`lower == upper`) apart; reading a term's value with `sentence.translate(theory)` and `model.eval`.
**Run:** `python model.py`
**Expected:** `Optimal makespan: 12`
