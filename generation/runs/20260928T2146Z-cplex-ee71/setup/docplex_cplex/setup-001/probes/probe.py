import sys, os, random, time
import cplex, docplex
from docplex.mp.model import Model
print("cplex", cplex.__version__, "docplex", docplex.__version__)
def trial(name, f):
    try: print(name, "->", f())
    except Exception as e: print(name, "-> RAISES", type(e).__name__, str(e)[:200])
def fresh():
    m = Model(); m.parameters.threads = 1; return m
# default gap knapsack (seed 17, n 40)
def knap(gap):
    rnd = random.Random(17); n = 40
    w = [rnd.randint(10**5, 10**6) for _ in range(n)]; v = [wi + rnd.randint(0, 10**4) for wi in w]
    m = fresh(); x = m.binary_var_list(n)
    m.add_constraint(m.sum(w[i]*x[i] for i in range(n)) <= sum(w)//2)
    m.maximize(m.sum(v[i]*x[i] for i in range(n)))
    if gap is not None: m.parameters.mip.tolerances.mipgap = gap
    s = m.solve(); d = m.solve_details
    return round(s.objective_value), d.status_code, d.status, round(d.best_bound), d.mip_relative_gap
trial("knapsack default gap", lambda: knap(None))
trial("knapsack gap 0", lambda: knap(0))
trial("mipgap default", lambda: fresh().parameters.mip.tolerances.mipgap.get())
trial("absmipgap default", lambda: fresh().parameters.mip.tolerances.absmipgap.get())
trial("integrality default", lambda: fresh().parameters.mip.tolerances.integrality.get())
# size limits
def size(nv, nc, ind=0):
    def f():
        m = fresh(); x = m.integer_var_list(nv, ub=3)
        for i in range(nc): m.add_constraint(x[i % nv] <= 3)
        b = m.binary_var_list(max(ind,1))
        for i in range(ind): m.add_indicator(b[i], x[i % nv] <= 1)
        s = m.solve(); return m.solve_details.status_code, m.solve_details.status
    return f
trial("1000 vars 1 constr", size(1000, 1))
trial("1001 vars 1 constr", size(1001, 1))
trial("10 vars 1000 constr", size(10, 1000))
trial("10 vars 1001 constr", size(10, 1001))
trial("10 vars 600 lin + 400 indicators (+1 bin var... total vars 410)", size(10, 600, 400))
trial("10 vars 600 lin + 401 indicators", size(10, 600, 401))
# satisfaction: objective detection
def sat():
    m = fresh(); x = m.integer_var(0, 3); m.add_constraint(x >= 1)
    r = (m.has_objective(), m.is_minimized(), str(m.objective_expr), type(m.objective_expr).__name__)
    s = m.solve(); return r, m.solve_details.status_code, m.solve_details.status
trial("satisfaction", sat)
def infeas():
    m = fresh(); x = m.integer_var(0, 3); m.add_constraint(x >= 5); s = m.solve(); return s, m.solve_details.status_code, m.solve_details.status
trial("infeasible", infeas)
def unb():
    m = fresh(); x = m.integer_var(0, m.infinity); m.maximize(x); s = m.solve(); return s is None, m.solve_details.status_code, m.solve_details.status
trial("unbounded", unb)
# market split timeout
def hard():
    m = fresh(); random.seed(1); rows = [[random.randint(0, 99) for _ in range(60)] for _ in range(6)]
    p = m.binary_var_list(60); sl = m.continuous_var_matrix(6, 2)
    for r, row in enumerate(rows): m.add_constraint(m.sum(a*p[j] for j, a in enumerate(row)) + sl[r,0] - sl[r,1] == sum(row)//2)
    m.minimize(m.sum(sl.values())); m.parameters.timelimit = 3
    s = m.solve(); return s is not None, m.solve_details.status_code, m.solve_details.status
trial("time limit", hard)
# operators
def neq():
    m = fresh(); x = m.integer_var(0, 3); y = m.integer_var(0, 3); c = (x != y); m.add(c); m.add(x == 1); m.add(y <= 1); s = m.solve(); return type(c).__name__, s and (s[x], s[y])
trial("x != y", neq)
def absf():
    m = fresh(); x = m.integer_var(-3, 3); y = m.integer_var(0, 3); m.add(y == m.abs(x - 1)); m.add(x == -2); s = m.solve(); return s[y]
trial("m.abs(x - 1)", absf)
def mx():
    m = fresh(); a = m.integer_var(-3, 3); b = m.integer_var(-3, 3); y = m.integer_var(-5, 5); m.add(y == m.max(a, b, 0)); m.add(a == -2); m.add(b == -1); s = m.solve(); return s[y]
trial("m.max", mx)
def prod():
    m = fresh(); x = m.integer_var(0, 5); y = m.integer_var(0, 5); m.add(x * y == 12); m.add(x >= y + 1); s = m.solve(); return s and (s[x], s[y]), m.solve_details.status
trial("x * y == 12", prod)
def logic():
    m = fresh(); a = m.binary_var(); b = m.binary_var(); x = m.integer_var(0, 5)
    m.add_equivalence(a, x >= 3); m.add(m.logical_or(a, b) == 1); m.add(b == 0); m.minimize(x); s = m.solve(); return s[x], s[a]
trial("equivalence / logical_or", logic)
def ifthen():
    m = fresh(); x = m.integer_var(0, 5); y = m.integer_var(0, 5); m.add_if_then(x >= 3, y == 0); m.add(x == 4); m.maximize(y); s = m.solve(); return s[y]
trial("add_if_then", ifthen)
def boolctx():
    m = fresh(); x = m.integer_var(0, 3); return bool(x == 1)
trial("bool(x == 1)", boolctx)
def floordiv():
    m = fresh(); x = m.integer_var(0, 3); return x // 2
trial("x // 2", floordiv)
def mod():
    m = fresh(); x = m.integer_var(0, 3); return x % 2
trial("x % 2", mod)
def expr_api():
    m = fresh(); x = m.integer_var(0, 3, name="x"); y = m.integer_var(0, 3, name="y"); e = 2*x + 3*y - 1
    return type(e).__name__, list((v.name, c) for v, c in e.iter_terms()), e.constant, type(x).__name__, type(2*x).__name__, [t.__name__ for t in type(2*x).__mro__][:4]
trial("expression API", expr_api)
def nsatobj():
    m = fresh(); x = m.integer_var(0, 3); m.minimize(0); return m.has_objective(), str(m.objective_expr)
trial("minimize(0)", nsatobj)
