Five of the nine instances (m = 12, 13, 16, 17, 20) end in `reference_timeout`:
the reference itself does not finish, so they are out of reach for any model of
this problem. CLP(FD) additionally runs out of its own budget on m = 8 while
solving m = 9 comfortably, which is the first-fail heuristic hitting a bad
branch rather than anything structural. Evidenced on m = 1, 4 and 9.
