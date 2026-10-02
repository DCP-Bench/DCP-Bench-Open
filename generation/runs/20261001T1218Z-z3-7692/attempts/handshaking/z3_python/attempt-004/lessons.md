# Lesson: unique answers and solution_limit 2 in z3_python

With a unique declared output (hil), the second solution of the enumeration is an UNSAT proof
over a highly symmetric problem. attempt-002 and attempt-003 (PbEq over degree literals, then
the implied pairing of degrees) found the first solution but timed out proving no second one on
the 18 person instance. Adding symmetry breaking on the interchangeable couples (order the two
spouses, order the couples by their first spouse's count) brought every instance to at most
2.5 s (attempt-004 evaluation.json). The symmetry breaking is the modeller's own, not the reference's.
