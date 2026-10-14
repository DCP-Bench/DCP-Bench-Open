import itertools
import gurobipy as gp
from gurobipy import GRB
def fresh():
    m = gp.Model(); m.Params.OutputFlag = 0; m.Params.Threads = 1; m.Params.MIPGap = 0; return m
fails = []
def expect(name, cond):
    if not cond: fails.append(name)
U = 3
# != : feasible iff a != b
for av, bv in itertools.product(range(U + 1), repeat=2):
    m = fresh(); a = m.addVar(ub=U, vtype=GRB.INTEGER); b = m.addVar(ub=U, vtype=GRB.INTEGER)
    before = m.addVar(vtype=GRB.BINARY)
    m.addConstr((before == 1) >> (a <= b - 1)); m.addConstr((before == 0) >> (a >= b + 1))
    m.addConstr(a == av); m.addConstr(b == bv); m.optimize()
    expect(f"neq {av},{bv}", (m.Status == GRB.OPTIMAL) == (av != bv))
# abs via aux
for av, bv in itertools.product(range(U + 1), repeat=2):
    m = fresh(); a = m.addVar(ub=U, vtype=GRB.INTEGER); b = m.addVar(ub=U, vtype=GRB.INTEGER); d = m.addVar(ub=U, vtype=GRB.INTEGER)
    diff = m.addVar(lb=-U, ub=U, vtype=GRB.INTEGER); m.addConstr(diff == a - b); m.addConstr(d == gp.abs_(diff))
    m.addConstr(a == av); m.addConstr(b == bv); m.optimize()
    expect(f"abs {av},{bv}", m.Status == GRB.OPTIMAL and round(d.X) == abs(av - bv))
# reified equality, both values of c forced
for av, bv, cv in itertools.product(range(U + 1), range(U + 1), (0, 1)):
    m = fresh(); a = m.addVar(ub=U, vtype=GRB.INTEGER); b = m.addVar(ub=U, vtype=GRB.INTEGER); c = m.addVar(vtype=GRB.BINARY)
    lt = m.addVar(vtype=GRB.BINARY); gt = m.addVar(vtype=GRB.BINARY)
    m.addConstr(lt + gt == 1 - c); m.addConstr((c == 1) >> (a == b))
    m.addConstr((lt == 1) >> (a <= b - 1)); m.addConstr((gt == 1) >> (a >= b + 1))
    m.addConstr(a == av); m.addConstr(b == bv); m.addConstr(c == cv); m.optimize()
    expect(f"reif {av},{bv},{cv}", (m.Status == GRB.OPTIMAL) == ((av == bv) == (cv == 1)))
# disjunction: x <= 1 or x >= 3 over 0..4
for xv in range(5):
    m = fresh(); x = m.addVar(ub=4, vtype=GRB.INTEGER); parts = [(x, 1), (3, x)]
    branch = m.addVars(len(parts), vtype=GRB.BINARY)
    for k, (left, right) in enumerate(parts): m.addConstr((branch[k] == 1) >> (left <= right))
    m.addConstr(branch.sum() >= 1); m.addConstr(x == xv); m.optimize()
    expect(f"disj {xv}", (m.Status == GRB.OPTIMAL) == (xv <= 1 or xv >= 3))
# all-different: count solutions of n=3 over 1..3 is 6
m = fresh(); n = mm = 3
x = m.addVars(n, lb=1, ub=mm, vtype=GRB.INTEGER)
pick = m.addVars(n, range(1, mm + 1), vtype=GRB.BINARY)
for i in range(n):
    m.addConstr(pick.sum(i, "*") == 1); m.addConstr(x[i] == gp.quicksum(v * pick[i, v] for v in range(1, mm + 1)))
for v in range(1, mm + 1): m.addConstr(pick.sum("*", v) <= 1)
m.Params.PoolSearchMode = 2; m.Params.PoolSolutions = 100; m.optimize()
sols = set()
for s in range(m.SolCount):
    m.Params.SolutionNumber = s; sols.add(tuple(round(x[i].Xn) for i in range(n)))
expect("alldiff count", len(sols) == 6 and all(len(set(t)) == 3 for t in sols))
# element and counting
table = [5, 7, 2, 9]
for iv in range(len(table)):
    m = fresh(); index = m.addVar(ub=3, vtype=GRB.INTEGER); value = m.addVar(ub=10, vtype=GRB.INTEGER)
    choose = m.addVars(len(table), vtype=GRB.BINARY); m.addConstr(choose.sum() == 1)
    m.addConstr(index == gp.quicksum(j * choose[j] for j in range(len(table))))
    m.addConstr(value == gp.quicksum(table[j] * choose[j] for j in range(len(table))))
    m.addConstr(index == iv); m.optimize()
    expect(f"element {iv}", m.Status == GRB.OPTIMAL and round(value.X) == table[iv])
# product of binary and integer in lo..hi
lo, hi = -2, 3
for bv, av in itertools.product((0, 1), range(lo, hi + 1)):
    m = fresh(); b = m.addVar(vtype=GRB.BINARY); a = m.addVar(lb=lo, ub=hi, vtype=GRB.INTEGER); p = m.addVar(lb=min(lo, 0), ub=max(hi, 0), vtype=GRB.INTEGER)
    m.addConstr(p <= hi * b); m.addConstr(p >= lo * b); m.addConstr(p <= a - lo * (1 - b)); m.addConstr(p >= a - hi * (1 - b))
    m.addConstr(a == av); m.addConstr(b == bv); m.optimize()
    expect(f"product {bv},{av}", m.Status == GRB.OPTIMAL and round(p.X) == bv * av)
# div / mod
k, hi2 = 3, 10
for av in range(hi2 + 1):
    m = fresh(); a = m.addVar(ub=hi2, vtype=GRB.INTEGER)
    q = m.addVar(lb=0, ub=hi2 // k, vtype=GRB.INTEGER); r = m.addVar(lb=0, ub=k - 1, vtype=GRB.INTEGER)
    m.addConstr(a == k * q + r); m.addConstr(a == av); m.optimize()
    expect(f"divmod {av}", m.Status == GRB.OPTIMAL and (round(q.X), round(r.X)) == divmod(av, k))
# max_ with constant, min_, and_, or_
for av, bv in itertools.product(range(-2, 3), repeat=2):
    m = fresh(); a = m.addVar(lb=-2, ub=2, vtype=GRB.INTEGER); b = m.addVar(lb=-2, ub=2, vtype=GRB.INTEGER)
    y = m.addVar(lb=-5, ub=5); z = m.addVar(lb=-5, ub=5)
    m.addConstr(y == gp.max_([a, b], constant=0)); m.addConstr(z == gp.min_(a, b))
    m.addConstr(a == av); m.addConstr(b == bv); m.optimize()
    expect(f"maxmin {av},{bv}", round(y.X) == max(av, bv, 0) and round(z.X) == min(av, bv))
for av, bv in itertools.product((0, 1), repeat=2):
    m = fresh(); a = m.addVar(vtype=GRB.BINARY); b = m.addVar(vtype=GRB.BINARY); z = m.addVar(vtype=GRB.BINARY); o = m.addVar(vtype=GRB.BINARY)
    m.addConstr(z == gp.and_(a, b)); m.addConstr(o == gp.or_(a, b)); m.addConstr(a == av); m.addConstr(b == bv); m.optimize()
    expect(f"andor {av},{bv}", round(z.X) == (av and bv) and round(o.X) == (av or bv))
# matrix api and tupledict helpers from the table
m = fresh(); v = m.addMVar((2, 3), vtype=GRB.BINARY); A = __import__("numpy").ones((1, 2)); m.addConstr(v.sum(axis=1) == 1); m.addConstr(A @ v[:, 0] <= 1); m.optimize()
expect("matrix", m.Status == GRB.OPTIMAL)
# lb defaults to 0
m = fresh(); w = m.addVar(vtype=GRB.INTEGER); m.update(); expect("lb default 0", w.LB == 0)
print("FAILED:", fails if fails else "none")
