import random, time
import gurobipy as gp
from gurobipy import GRB
def knap(seed, n, gap):
    rnd = random.Random(seed)
    w = [rnd.randint(10**5, 10**6) for _ in range(n)]
    v = [wi + rnd.randint(0, 10**4) for wi in w]
    m = gp.Model(); m.Params.OutputFlag = 0; m.Params.Threads = 1
    if gap is not None: m.Params.MIPGap = gap
    x = m.addVars(n, vtype=GRB.BINARY)
    m.addConstr(gp.quicksum(w[i]*x[i] for i in range(n)) <= sum(w)//2)
    m.setObjective(gp.quicksum(v[i]*x[i] for i in range(n)), GRB.MAXIMIZE)
    m.Params.TimeLimit = 20
    t=time.time(); m.optimize()
    return m.Status, round(m.ObjVal), round(m.ObjBound), round(time.time()-t,2)
found = 0
for seed in range(300):
    for n in (40, 60):
        d = knap(seed, n, None)
        if d[1] == d[2]: continue
        z = knap(seed, n, 0)
        if d[1] != z[1]:
            print(seed, n, "default", d, "gap0", z, flush=True); found += 1
    if found >= 5: break
print("done", seed)
