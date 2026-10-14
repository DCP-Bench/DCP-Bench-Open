# Plan: four_numbers (gecode_cpp, attempt-001)

Output x: three integers, each 1..10.

Requirement: every given number is a sum of a non-empty subset of x.
  -> seven subset sums of x (x0, x1, x2, and the 4 two-or-three element sums) as IntVars via expr(sum(...)),
     then for each given number r: member(*this, sums, IntVar(r, r), IPL_DOM) (r is one of the subset sums)

Requirement: the three numbers are between 1 and 10 inclusive.
  -> IntVarArray x(*this, 3, 1, 10)

Requirement: subset sums are defined by the chosen numbers (no decomposition needed beyond expr).
  -> linear sums via expr(*this, sum(...)), IPL default (bounds) is enough for seven sums of three variables.

Branching: branch on x in order with INT_VAR_SIZE_MIN / INT_VAL_MIN (domains are tiny).
Objective: none (satisfaction). Output x.
