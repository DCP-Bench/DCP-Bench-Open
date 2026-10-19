# Cryptarithm (SEND + MORE = MONEY)

**Problem:** Assign distinct digits to the letters of SEND + MORE = MONEY, with no leading zero.
**Shows:** letters as integer variables with bounds, `AllDifferent` over them, a data-driven linear equation built from powers of ten, lower bounds for leading letters, reading and checking the solution.
**Run:** `julia model.jl`
**Expected:** `Status: OPTIMAL`
**Expected:** `D=7 E=5 M=1 N=6 O=0 R=8 S=9 Y=2`
**Expected:** `Check: true`
