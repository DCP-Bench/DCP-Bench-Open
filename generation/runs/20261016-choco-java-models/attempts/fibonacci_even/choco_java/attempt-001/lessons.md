m.isEq(x, v) already returns a BoolVar, so no .getVar() is needed.
For the AND of two 0/1 flags, m.times(a, b, c) on BoolVars is simpler than arithm with "*".
The instance has no fields, so the starting terms 1 and 2 and the four-million limit come from the description.
