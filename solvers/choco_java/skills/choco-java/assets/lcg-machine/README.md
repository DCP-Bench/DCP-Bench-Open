# One machine with release times (lazy clause generation)

**Problem:** three tasks of durations 2, 3 and 2 on one machine, released at times 0, 0 and 4, one task at a time. Minimise the makespan.
**Shows:** lazy clause generation switched on with `new Model(name, SettingsBuilder.init().setLCG(true))`, on a model whose constraints are all on the checked list (`cumulative` with unit heights, `arithm`, `max`), and the proof check.
**Run:** `java Machine.java`
**Expected:** `Makespan: 7`
