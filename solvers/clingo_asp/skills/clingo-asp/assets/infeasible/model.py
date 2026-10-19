"""Pigeonhole: put three pigeons into two holes, one pigeon per hole. No such placement exists."""
import clingo

PROGRAM = """
% Each pigeon sits in exactly one hole.
1 { in(P,H) : hole(H) } 1 :- pigeon(P).

% No hole holds two pigeons.
:- in(P1,H), in(P2,H), P1 < P2.

#show in/2.
"""

ctl = clingo.Control()
ctl.add("base", [], PROGRAM)
ctl.add("base", [], "pigeon(1..3).\nhole(1..2).\n")
ctl.ground([("base", [])])

with ctl.solve(yield_=True) as handle:
    models = [m for m in handle]
    result = handle.get()

print("Satisfiable:", result.satisfiable)
print("Unsatisfiable:", result.unsatisfiable)
print("Models found:", len(models))
