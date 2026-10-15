"""Enumerate every switch setting that satisfies the rules, by blocking each one found."""
from itertools import product

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

SWITCHES = ["a", "b", "c", "d", "e"]

pool = IDPool()
on = {name: pool.id(name) for name in SWITCHES}

cnf = CNF()
cnf.extend(CardEnc.atmost(lits=list(on.values()), bound=2, vpool=pool,
                          encoding=EncType.seqcounter).clauses)  # at most two on
cnf.append([-on["a"], on["b"]])                                  # a on -> b on
cnf.append([on["c"], on["d"], on["e"]])                          # one of c, d, e on

solutions = []
with Solver(name="glucose42", bootstrap_with=cnf.clauses) as solver:
    while solver.solve():
        true_lits = {lit for lit in solver.get_model() if lit > 0}
        setting = tuple(on[name] in true_lits for name in SWITCHES)
        solutions.append(setting)
        # Block this setting of the declared switches; auxiliary variables may differ.
        solver.add_clause([-on[name] if value else on[name]
                           for name, value in zip(SWITCHES, setting)])

brute = [s for s in product([False, True], repeat=len(SWITCHES))
         if sum(s) <= 2 and (not s[0] or s[1]) and (s[2] or s[3] or s[4])]

for setting in solutions:
    print("on:", [n for n, v in zip(SWITCHES, setting) if v])
print("Total solutions:", len(solutions))
print("Distinct:", len(set(solutions)) == len(solutions))
print("Matches brute force:", sorted(solutions) == sorted(brute))
