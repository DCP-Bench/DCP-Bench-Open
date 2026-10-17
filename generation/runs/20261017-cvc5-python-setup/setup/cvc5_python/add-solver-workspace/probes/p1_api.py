import traceback
from cvc5.pythonic import *

def attempt(label, fn):
    try:
        r = fn()
        print(f"[ok] {label}: {r}")
    except Exception as e:
        print(f"[err] {label}: {type(e).__name__}: {str(e)[:300]}")

# basic satisfy
x, y = Ints("x y")
s = Solver()
s.add(x >= 0, x <= 10, y >= 0, y <= 10, x + y == 7, x - y == 1)
r = s.check()
print("basic:", r, s.model()[x], s.model()[y], type(s.model()[x]))

# Sum over Booleans
bs = Bools("b0 b1 b2")
attempt("Sum(bools)", lambda: Sum(list(bs)))
attempt("sum() python builtin on bools", lambda: sum(bs))
attempt("Sum(If)", lambda: Sum([If(b, 1, 0) for b in bs]))
attempt("PbEq", lambda: PbEq([(b, 1) for b in bs], 1))
attempt("AtMost", lambda: AtMost(*bs, 1))
attempt("AtLeast", lambda: AtLeast(*bs, 1))
attempt("PbLe", lambda: PbLe([(b, 1) for b in bs], 1))

# set options
s2 = Solver()
attempt("set timeout", lambda: s2.set("timeout", 1000))
attempt("set tlimit-per", lambda: s2.set("tlimit-per", 1000))
attempt("set produce-models", lambda: s2.set("produce-models", True))
attempt("set incremental", lambda: s2.set("incremental", True))
attempt("set random-seed", lambda: s2.set("random-seed", 3))
attempt("set bogus option", lambda: s2.set("bogus-option-xyz", 1))
attempt("SolverFor QF_LIA", lambda: SolverFor("QF_LIA").check())
attempt("SolverFor QF_NIA", lambda: SolverFor("QF_NIA").check())
attempt("SolverFor bogus logic", lambda: SolverFor("NOTALOGIC").check())
attempt("SimpleSolver", lambda: SimpleSolver().check())

# unsat and unknown
s3 = Solver()
s3.add(x > 3, x < 2)
print("unsat:", s3.check())
attempt("model after unsat", lambda: s3.model())
attempt("reason_unknown after unsat", lambda: s3.reason_unknown())

# nonlinear
a, b = Ints("a b")
s4 = Solver()
s4.add(a * b == 143, a > 1, b > 1)
r4 = s4.check()
print("nonlinear:", r4, s4.reason_unknown())

# ints with no bounds, linear: sat
s5 = Solver()
s5.add(x + y == 1000001)
print("unbounded linear:", s5.check())

# pythonic model value types
s6 = Solver()
s6.add(x == 5, bs[0] == True, bs[1] == False)
s6.check()
m = s6.model()
print("model x:", m[x], m.eval(x, model_completion=True).as_long(), is_true(m.eval(bs[0], model_completion=True)))
attempt("model[bool]", lambda: m[bs[0]])
attempt("model[unused var] model_completion", lambda: m.eval(Int('zz'), model_completion=True))
attempt("model[unused var]", lambda: m[Int('zz')])

# python bool in if
attempt("if on symbolic", lambda: bool(x == 3))

# Distinct
d = Ints("d0 d1 d2")
s7 = Solver()
s7.add(Distinct(d), *[And(v >= 0, v < 2) for v in d])
print("distinct 3 in 0..1:", s7.check())
attempt("Distinct empty", lambda: Distinct([]))
attempt("Distinct single", lambda: Distinct([x]))

# Min/max
attempt("Max builtin", lambda: Max([x, y]))

# Quantifiers
i = Int("i")
s8 = Solver()
s8.add(ForAll([i], Implies(And(i >= 0, i < 3), x >= i)), x <= 2, x >= 0)
print("forall sat:", s8.check())
attempt("forall model x", lambda: s8.model()[x])
s9 = Solver()
s9.add(ForAll([i], Implies(And(i >= 0, i < 3), x > i)), x <= 2, x >= 0)
print("forall unsat:", s9.check())
s10 = Solver()
s10.add(Exists([i], And(i * 2 == x, i > 0)), x == 6)
print("exists sat:", s10.check())
s11 = Solver()
s11.add(Exists([i], And(i * 2 == x, i > 0)), x == 5)
print("exists unsat (parity):", s11.check())
