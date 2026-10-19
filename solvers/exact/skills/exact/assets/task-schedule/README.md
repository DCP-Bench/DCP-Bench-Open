# Four tasks on one machine (scheduling)

**Problem:** Four tasks with durations 3, 2, 4, 2 share one machine; task 0 must finish before task 2 starts, and task 2 is released at time 5. Minimise the makespan.
**Shows:** start-time variables with release bounds; precedence as a linear constraint; no-overlap between tasks built with two reified orderings per pair; minimising the makespan.
**Run:** `python3 model.py`
**Expected:** `Makespan: 11`
