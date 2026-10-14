import gurobipy as gp
from gurobipy import GRB
def fresh():
    m = gp.Model(); m.Params.OutputFlag = 0; m.Params.Threads = 1; return m
def trial(name, f):
    try: print(name, "->", f())
    except Exception as e: print(name, "-> RAISES", e)
def gen(k_abs, k_lin, n_vars=1000):
    def f():
        m = fresh(); x = m.addVars(n_vars // 2, lb=-3, ub=3, vtype=GRB.INTEGER); a = m.addVars(n_vars // 2, ub=3, vtype=GRB.INTEGER)
        for i in range(k_abs): m.addConstr(a[i % (n_vars//2)] == gp.abs_(x[i % (n_vars//2)]))
        for i in range(k_lin): m.addConstr(x[i % (n_vars//2)] <= 3)
        m.optimize(); return m.Status
    return f
trial("500 abs_ + 1499 linear (1999 total)", gen(500, 1499))
trial("500 abs_ + 1501 linear (2001 total)", gen(500, 1501))
def ind(k_ind, k_lin):
    def f():
        m = fresh(); x = m.addVars(500, ub=3, vtype=GRB.INTEGER); b = m.addVars(500, vtype=GRB.BINARY)
        for i in range(k_ind): m.addGenConstrIndicator(b[i % 500], True, x[i % 500], GRB.LESS_EQUAL, 1)
        for i in range(k_lin): m.addConstr(x[i % 500] <= 3)
        m.optimize(); return m.Status
    return f
trial("1000 indicator + 999 linear", ind(1000, 999))
trial("1000 indicator + 1001 linear", ind(1000, 1001))
def nl(n):
    def f():
        m = fresh(); v = m.addVars(n, ub=3, vtype=GRB.INTEGER); y = m.addVar(ub=100)
        m.addGenConstrNL(y, v[0] * v[0] * v[0]); m.addConstr(v.sum() >= 1); m.optimize(); return m.Status
    return f
trial("NL cube with 199 vars + aux", nl(199))
trial("NL cube with 300 vars + aux", nl(300))
def pw(n):
    def f():
        m = fresh(); v = m.addVars(n, ub=3, vtype=GRB.INTEGER); y = m.addVar(ub=100)
        m.addGenConstrPow(v[0], y, 3); m.addConstr(v.sum() >= 1); m.optimize(); return m.Status
    return f
trial("addGenConstrPow with 300 vars", pw(300))
