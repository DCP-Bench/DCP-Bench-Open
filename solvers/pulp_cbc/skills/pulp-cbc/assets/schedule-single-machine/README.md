# Single-machine schedule (scheduling, no overlap)

**Problem:** Four jobs with durations 3, 2, 4, 2 share one machine; minimise the sum of completion times.
**Shows:** start and end variables, a binary per pair of jobs choosing the order, a big-M from the horizon (sum of durations), minimise over end times.
**Run:** `python3 model.py`
**Expected:** `Status: Optimal`
**Expected:** `Total completion time: 24`
