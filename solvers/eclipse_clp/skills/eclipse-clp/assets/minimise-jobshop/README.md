# Job shop (minimise makespan)

**Problem:** 3 jobs on 3 machines, each job visits the machines in a fixed order; minimise the makespan.
**Shows:** one `disjunctive/2` per machine from `lib(ic_edge_finder)`, precedences as `#=<`, `max/1` in a makespan constraint, `bb_min/3`. Start and duration lists are built by plain recursion, because `findall/3` would copy the variables.
**Run:** `eclipse.exe -f model.ecl -e main` (`eclipse.exe` must be on PATH, or call it by its full path)
**Expected:** `Makespan: 10`
**Expected:** `job 1: [1:0+3, 2:3+2, 3:8+2]`
One line per job, each task as `machine:start+duration`.
**Time:** about 0.3 s wall, start-up included.
