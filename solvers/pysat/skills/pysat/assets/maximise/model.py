"""Assign three workers to three jobs, one each, to maximise total profit."""
from itertools import permutations

from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2Stratified
from pysat.formula import IDPool, WCNF

PROFIT = [  # PROFIT[worker][job]
    [7, 3, 5],
    [4, 8, 2],
    [6, 1, 9],
]
N = len(PROFIT)

pool = IDPool()
x = [[pool.id(("x", w, j)) for j in range(N)] for w in range(N)]

wcnf = WCNF()
for w in range(N):                       # hard: each worker takes exactly one job
    wcnf.extend(CardEnc.equals(lits=x[w], bound=1, vpool=pool,
                               encoding=EncType.seqcounter).clauses)
for j in range(N):                       # hard: each job goes to at most one worker
    wcnf.extend(CardEnc.atmost(lits=[x[w][j] for w in range(N)], bound=1, vpool=pool,
                               encoding=EncType.seqcounter).clauses)
# Maximising profit = minimising the profit that is NOT collected. The soft clause
# [x] with weight p is falsified, and paid, exactly when the pair is not chosen.
# So the best cost is total - (maximum profit).
total = sum(map(sum, PROFIT))
for w in range(N):
    for j in range(N):
        wcnf.append([x[w][j]], weight=PROFIT[w][j])

rc2 = RC2Stratified(wcnf, solver="glucose42")
model = rc2.compute()
true_lits = {lit for lit in model if lit > 0}
assignment = [next(j for j in range(N) if x[w][j] in true_lits) for w in range(N)]
profit = sum(PROFIT[w][assignment[w]] for w in range(N))
print("Assignment (worker -> job):", assignment)
print("Maximum profit:", profit)
print("Matches brute force:", profit == max(sum(PROFIT[w][p[w]] for w in range(N))
                                              for p in permutations(range(N))))
print("Cost agrees:", total - rc2.cost == profit)
rc2.delete()
