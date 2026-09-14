Five of the nine instances (m = 12, 13, 16, 17, 20) end in `reference_timeout`:
the CPMpy reference itself does not finish inside the 180 s reference budget, so
no model of this problem can be evidenced on them. The same five were already
unreachable for the accepted z3_python and clingo_asp models. Coverage for this
pair is therefore m = 8, 1, 4 and 9 for CPMpy and CP-SAT; Gecode also runs out
of its own 180 s execution budget on m = 13, leaving it three instances.
