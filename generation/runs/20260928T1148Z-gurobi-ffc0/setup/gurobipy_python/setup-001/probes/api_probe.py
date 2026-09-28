import gurobipy as gp
from gurobipy import GRB
def fresh():
    m = gp.Model(); m.Params.OutputFlag = 0; m.Params.Threads = 1; m.Params.MIPGap = 0; return m
def trial(name, f):
    try: print(name, "->", f())
    except Exception as e: print(name, "-> RAISES", type(e).__name__, e)
# != support
def neq():
    m = fresh(); x = m.addVar(vtype=GRB.INTEGER, ub=3); y = m.addVar(vtype=GRB.INTEGER, ub=3); m.addConstr(x != y); return "accepted"
trial("x != y", neq)
# abs_, max_, min_, and_, or_, indicator shorthand
def gens():
    m = fresh(); x = m.addVar(lb=-5, ub=5, vtype=GRB.INTEGER); a = m.addVar(ub=10, vtype=GRB.INTEGER)
    m.addConstr(a == gp.abs_(x)); m.addConstr(x == -3); m.optimize(); r = [a.X]
    b = m.addVars(3, vtype=GRB.BINARY); z = m.addVar(vtype=GRB.BINARY); o = m.addVar(vtype=GRB.BINARY)
    m.addConstr(z == gp.and_(b[0], b[1])); m.addConstr(o == gp.or_(b[0], b[2]))
    mx = m.addVar(lb=-10, ub=10); m.addConstr(mx == gp.max_([x, a], constant=0))
    mn = m.addVar(lb=-10, ub=10); m.addConstr(mn == gp.min_(x, a))
    m.addConstr((b[0] == 1) >> (x + a <= 0)); m.addConstr(b[1] == 1); m.addConstr(b[2] == 0)
    m.optimize(); return r, m.Status, z.X, o.X, mx.X, mn.X, b[0].X
trial("abs_/and_/or_/max_/min_/indicator", gens)
# gen constr with expression argument
def absexpr():
    m = fresh(); x = m.addVar(ub=5, vtype=GRB.INTEGER); y = m.addVar(ub=5, vtype=GRB.INTEGER); d = m.addVar(ub=5)
    m.addConstr(d == gp.abs_(x - y)); return "accepted"
trial("abs_(x - y)", absexpr)
# products
def prod():
    m = fresh(); x = m.addVar(ub=5, vtype=GRB.INTEGER); y = m.addVar(ub=5, vtype=GRB.INTEGER)
    m.addConstr(x * y == 12); m.addConstr(x >= y + 1); m.optimize(); return m.Status, x.X, y.X, type(x*y).__name__
trial("x*y == 12 (nonconvex quadratic)", prod)
# quadratic size limit: 201 vars + one product
def quadlimit():
    m = fresh(); v = m.addVars(201, vtype=GRB.INTEGER, ub=3); m.addConstr(v[0] * v[1] <= 4); m.addConstr(v.sum() >= 2); m.optimize(); return m.Status
trial("201 vars with a quadratic constraint", quadlimit)
def quadlimit2():
    m = fresh(); v = m.addVars(199, vtype=GRB.INTEGER, ub=3); m.addConstr(v[0] * v[1] <= 4); m.addConstr(v.sum() >= 2); m.optimize(); return m.Status
trial("199 vars with a quadratic constraint", quadlimit2)
# does a gen constr abs_ count as a linear constraint towards 2000 ? 1500 vars, 1500 abs gen constrs + 1000 linear
def genlimit():
    m = fresh(); x = m.addVars(750, lb=-3, ub=3, vtype=GRB.INTEGER); a = m.addVars(750, ub=3, vtype=GRB.INTEGER)
    for i in range(750): m.addConstr(a[i] == gp.abs_(x[i]))
    for i in range(1500): m.addConstr(x[i % 750] <= 3)
    m.optimize(); return m.Status, m.NumConstrs, m.NumGenConstrs
trial("1500 vars, 750 abs_ + 1500 linear", genlimit)
# division / modulo
def div():
    m = fresh(); x = m.addVar(ub=5, vtype=GRB.INTEGER); return x / 2, x // 2
trial("x / 2 and x // 2", div)
def mod():
    m = fresh(); x = m.addVar(ub=5, vtype=GRB.INTEGER); return x % 2
trial("x % 2", mod)
# tupledict helpers
def td():
    m = fresh(); x = m.addVars(2, 3, vtype=GRB.BINARY, name="x"); return type(x).__name__, x.sum(0, "*"), len(x.select(1, "*"))
trial("tupledict sum/select", td)
# objective with no terms
def emptyobj():
    m = fresh(); m.addVar(); m.update(); o = m.getObjective(); return type(o).__name__, o.size(), m.ModelSense, m.NumObj
trial("empty objective", emptyobj)
# setObjective with constant
def constobj():
    m = fresh(); m.addVar(); m.setObjective(0); m.update(); o = m.getObjective(); return o.size(), m.NumObj
trial("setObjective(0)", constobj)
# Var in bool context
def boolctx():
    m = fresh(); x = m.addVar(); return bool(x == 1)
trial("bool(x == 1)", boolctx)
# addConstr with a python bool
def pybool():
    m = fresh(); x = m.addVar(); m.addConstr(True); return "accepted"
trial("addConstr(True)", pybool)
# nlfunc availability
trial("gp.nlfunc", lambda: [n for n in dir(gp.nlfunc) if not n.startswith("_")][:12])
def nl():
    m = fresh(); x = m.addVar(lb=1, ub=6, vtype=GRB.INTEGER); y = m.addVar(lb=0, ub=100)
    m.addGenConstrNL(y, x * x * x); m.addConstr(y == 27); m.optimize(); return m.Status, x.X
trial("addGenConstrNL cube", nl)
