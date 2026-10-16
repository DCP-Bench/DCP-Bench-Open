# Plan: circular_table_averbach_1_2 (satisfaction, no objective)

Seats are 0, 1, 2 around the table; seat p passes to seat p+1 mod 3 (the person on the right).

- X, Y and Z sit in three different seats -> distinct(*this, {x, y, z}, IPL_DOM)
- American, English and French are in three different seats -> distinct(*this, {american, english, french}, IPL_DOM)
- Y passed three hearts to the American, so the American sits on Y's right: american = (y+1) mod 3 -> element(*this, IntArgs({1,2,0}), y, american) [table is domain consistent]
- X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman. That passer sits at french-1, and X passes to x+1, so french = (x+2) mod 3 -> element(*this, IntArgs({2,0,1}), x, french)
- Branching: all six variables, INT_VAR_SIZE_MIN, INT_VAL_MIN (domains are 0..2, so this is complete).
- Objective: none, satisfaction.
