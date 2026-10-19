# Cryptarithm (satisfy, weighted sum)

**Problem:** letters stand for distinct digits; SEND + MORE = MONEY, and AB + AB = AAA (no solution).
**Shows:** string constants for uppercase letters (`letter("S")`, printed back as `.string`), a `#sum` with negative weights compared with `!= 0`, the tuple rule (each tuple carries its letter), reading one model from a loop with the default `models = 1`, and `SolveResult.unsatisfiable`.
**Run:** `python3 model.py`
**Expected:** `SEND + MORE = MONEY -> D=7 E=5 M=1 N=6 O=0 R=8 S=9 Y=2`
**Expected:** `AB + AB = AAA -> no solution, unsatisfiable: True`
