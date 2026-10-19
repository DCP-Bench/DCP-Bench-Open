"""Choose a committee of three from six people under two conflicts (SAT, one solve)."""
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

PEOPLE = ["Ann", "Bob", "Cem", "Dana", "Eli", "Fay"]
CONFLICTS = [("Ann", "Bob"), ("Cem", "Dana")]  # never on the same committee

pool = IDPool()
seat = {person: pool.id(person) for person in PEOPLE}

cnf = CNF()
for a, b in CONFLICTS:
    cnf.append([-seat[a], -seat[b]])
cnf.extend(CardEnc.equals(lits=list(seat.values()), bound=3, vpool=pool,
                          encoding=EncType.seqcounter).clauses)

with Solver(name="glucose42", bootstrap_with=cnf.clauses) as solver:
    if not solver.solve():
        print("UNSATISFIABLE")
    else:
        true_lits = {lit for lit in solver.get_model() if lit > 0}
        chosen = [p for p in PEOPLE if seat[p] in true_lits]
        print("Committee:", ", ".join(chosen))
        print("Size:", len(chosen))
        print("Conflicts respected:", all(not (a in chosen and b in chosen) for a, b in CONFLICTS))
