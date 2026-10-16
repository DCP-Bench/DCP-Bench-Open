# Reading a JSON instance (no JSON library)

**Problem:** read the instance file `instance.json` given as a command-line argument and report its name and total weight.
**Shows:** `main(Args)` with a file argument, a hand-written JSON reader for objects, arrays, integers and strings, `:-` clauses for predicates with output arguments, character codes with `ord/1`.
**Run:** `picat model.pi instance.json`
**Expected:** `name: demo`
**Expected:** `total weight: 15`
