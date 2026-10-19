from cvc5.pythonic import *

# quick start
x, y = Ints("x y")
s = SolverFor("QF_LIA")
s.add(x >= 0, x <= 10, y >= 0, y <= 10, x + y == 7, x - y == 1)
if s.check() == sat:
    m = s.model()
    print("quick:", m[x], m[y], m.eval(x, model_completion=True).as_long())

# reification with Bool == comparison
b = Bool("b")
s = SolverFor("QF_LIA")
s.add(x >= 0, x <= 6, b == (x > 3), Not(b))
print("reify (expect sat x<=3):", s.check(), s.model().eval(x, model_completion=True).as_long())

s = SolverFor("QF_LIA")
s.add(x >= 0, x <= 6, b == (x > 3), b)
print("reify (expect unsat? x>3 and b):", s.check())
print("reify (expect sat with x>3):", end=" ")
s = SolverFor("QF_LIA")
s.add(x >= 0, x <= 6, b == (x > 3), b, x <= 4)
print(s.check(), s.model().eval(x, model_completion=True).as_long())

# Bools list, Xor, Implies
bs = Bools(["p", "q", "r"])
s = SolverFor("QF_LIA")
s.add(Xor(bs[0], bs[1]), Implies(bs[0], bs[2]), Not(bs[2]))
print("bools:", s.check(), [is_true(s.model().eval(v, model_completion=True)) for v in bs])

# Sum of If with ==
s = SolverFor("QF_LIA")
s.add(Sum([If(v, 1, 0) for v in bs]) == 2)
print("card==2:", s.check(), [is_true(s.model().eval(v, model_completion=True)) for v in bs])

# Or over a list, And over a list
s = SolverFor("QF_LIA")
s.add(Or([x == 1, x == 2]), x >= 2)
print("or-list:", s.check(), s.model().eval(x, model_completion=True).as_long())

# Ints with a list
xs = Ints(["a", "b"])
print("Ints list:", xs)

# bool() on symbolic
print("bool(sym) is", bool(x == 3))

# Solver.add with list raises; check if s.add(*list) fine
s = SolverFor("QF_LIA")
s.add(*[x >= 1, x <= 2])
print("star add:", s.check())

# Solver() vs SolverFor on same problem with ints
s = Solver()
s.add(x > 0, x < 3)
print("default solver:", s.check())

# model()[x] for var not in formula
s = Solver()
s.add(x > 0)
s.check()
print("unused:", s.model()[Int("unused_var")])

# tlimit-per honored
s = SolverFor("QF_LIA")
s.set("tlimit-per", 500)
print("tlimit-per set ok")

# produce-models needed?
s = Solver()
s.add(x == 4)
print("no produce-models:", s.check(), s.model()[x])
