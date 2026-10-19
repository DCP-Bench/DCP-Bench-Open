# Staffing with too few people (infeasible)

**Problem:** cover 3 shifts with 2 people each from 5 people, with at most one shift per person. Six places, five people: no plan exists.
**Shows:** `binary_var_matrix` keyed by (person, shift), reading the status of an infeasible model without an exception.
**Run:** `python3 model.py`
**Expected:** `No staffing plan exists: integer infeasible`
