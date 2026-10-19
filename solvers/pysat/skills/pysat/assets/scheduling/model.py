"""Single machine: order jobs with release times and one precedence, minimise the makespan."""
from itertools import permutations

from pysat.examples.rc2 import RC2Stratified
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine

DURATION = [3, 2, 4, 2]
RELEASE = [0, 1, 0, 5]        # a job may not start before its release time
BEFORE = [(0, 2)]             # job 0 must finish before job 2 starts
HORIZON = sum(DURATION) + max(RELEASE)
N = len(DURATION)

pool = IDPool()
start = [Integer(f"s{j}", RELEASE[j], HORIZON - DURATION[j], vpool=pool) for j in range(N)]
makespan = Integer("makespan", 0, HORIZON, vpool=pool)
engine = IntegerEngine(vars=start + [makespan], vpool=pool)

for j in range(N):                            # every job ends by the makespan
    engine.add_linear(start[j] + DURATION[j] <= makespan)
no_overlap = []                               # one selector per pair: i before j, or j before i
for i in range(N):
    for j in range(i + 1, N):
        i_first = engine.add_linear(start[i] + DURATION[i] <= start[j], reified=True)
        j_first = engine.add_linear(start[j] + DURATION[j] <= start[i], reified=True)
        no_overlap.append([i_first, j_first])
for i, j in BEFORE:
    engine.add_linear(start[i] + DURATION[i] <= start[j])

formula = WCNF()
formula.extend(engine.clausify().clauses)     # hard: the constraints
for clause in no_overlap:
    formula.append(clause)
for t in range(1, HORIZON + 1):               # soft: pay t when the makespan is t
    formula.append([-makespan.equals(t)], weight=t)

rc2 = RC2Stratified(formula, solver="glucose42")
model = rc2.compute()
dense = [-v for v in range(1, pool.top + 1)]  # RC2 omits unused variables; Integer.decode needs all
for lit in model:
    dense[abs(lit) - 1] = lit
times = [s.decode(dense) for s in start]
span = makespan.decode(dense)
proven = rc2.cost == span
rc2.delete()


def brute_force():
    """Best makespan over all job orders, each job started as early as possible."""
    best = None
    for order in permutations(range(N)):
        clock, end = 0, {}
        for j in order:
            clock = max(clock, RELEASE[j]) + DURATION[j]
            end[j] = clock
        if all(end[i] <= end[j] - DURATION[j] for i, j in BEFORE):
            best = clock if best is None else min(best, clock)
    return best


print("Start times:", times)
print("Makespan:", span)
print("Optimal:", proven)
print("Matches brute force:", span == brute_force())
