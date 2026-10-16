"""Four pigeons into three holes: no assignment exists, for a CNF and for a WCNF."""
from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2Stratified
from pysat.formula import CNF, IDPool, WCNF
from pysat.solvers import Solver

PIGEONS, HOLES = 4, 3

pool = IDPool()
slot = {(p, h): pool.id((p, h)) for p in range(PIGEONS) for h in range(HOLES)}

cnf = CNF()
for p in range(PIGEONS):                        # each pigeon in exactly one hole
    cnf.extend(CardEnc.equals(lits=[slot[p, h] for h in range(HOLES)], bound=1,
                              vpool=pool, encoding=EncType.seqcounter).clauses)
for h in range(HOLES):                          # each hole holds at most one pigeon
    cnf.extend(CardEnc.atmost(lits=[slot[p, h] for p in range(PIGEONS)], bound=1,
                              vpool=pool, encoding=EncType.seqcounter).clauses)

with Solver(name="glucose42", bootstrap_with=cnf.clauses) as solver:
    print("CNF status:", "SATISFIABLE" if solver.solve() else "UNSATISFIABLE")

# The same hard clauses with a soft clause per slot: an unsatisfiable hard part
# makes RC2 return None rather than a cost.
wcnf = WCNF()
wcnf.extend(cnf.clauses)
for lit in slot.values():
    wcnf.append([-lit], weight=1)
rc2 = RC2Stratified(wcnf, solver="glucose42")
print("WCNF model:", "none" if rc2.compute() is None else "found")
rc2.delete()
