Requirement: "Requires exactly m values in x to take one of the values in v."
  -> count(*this, x, IntSet(v), IRT_EQ, m, IPL_DOM)  [global count with a set of values]
Requirement: "All other values may be anything larger than or equal to 0 and less than or equal to 7."
  -> x declared with domain 0..7 (problem constant from the description)
Branching: branch on x with INT_VAR_SIZE_MIN, INT_VAL_MIN (x is the only decision variable).
Objective: none (satisfaction). Output x.
