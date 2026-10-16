mark positions: "a_1 = 0 < a_2 < ... < a_m" -> marks[0] = 0 (arithm "="), m.increasing(marks, 1)
the m marks on an integer line, mark 0 at position 0 -> marks[i] in 0..ub, ub from the 2^(m-1)-1 ruler
the m(m-1)/2 differences a_j - a_i, 1 <= i < j <= m -> one diff var per pair, scalar linear equality
the differences are distinct -> m.allDifferent(diffs, "AC").post()
the length of the ruler is a_m -> marks[m-1] (output "length")
minimise the length (minimum length ruler) -> m.setObjective(MINIMIZE, marks[m-1])
print the positions of the marks -> out.put("marks", marks), out.put("length", marks[m-1])
reflection of a ruler is a ruler -> symmetry break a_2 < a_m - a_{m-1} (an extra constraint, not a requirement; valid for any ruler)
search for the proof (not in the description) -> domOverWDeg on marks, Luby restarts
