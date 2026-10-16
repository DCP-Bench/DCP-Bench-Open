Actor accepts a set of movie offers, each a first and last filming day; no two accepted offers may overlap; maximise the number accepted.
  -> one machine (the actor), each movie an optional task with fixed start s_i = first day and duration e_i - s_i + 1 (days are inclusive): unary(*this, starts, durations, sel, IPL_DEF)
  Overlap of two movies (sharing a day) is exactly "the two tasks cannot both run on the unary resource". Distinct endpoints in all instances, so touching intervals do not arise; the +1 makes day-inclusive semantics exact anyway.
Output selected_movies[i] = sel[i] (1 if movie i is accepted, 0 otherwise).
Objective: maximise total = sum(sel) -> maximize(total), total = expr(*this, sum(sel)).
Branching: branch on sel (BOOL_VAR_NONE, BOOL_VAL_MAX) so the search tries to accept each movie first; no other decision variables.
