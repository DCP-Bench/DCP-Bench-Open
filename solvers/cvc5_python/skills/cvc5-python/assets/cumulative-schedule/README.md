# Renewable resource (cumulative, minimise makespan)

**Problem:** 5 tasks with durations and resource demands share a resource of capacity 4. Minimise the makespan. Data in `data.json`.
**Shows:** a cumulative constraint written per time point, `Sum(If(And(start <= t, t < start + dur), demand, 0)) <= capacity`, minimisation by tightening.
**Run:** `python model.py` (or `python model.py other.json`)
**Expected:** `Optimal makespan: 7`
