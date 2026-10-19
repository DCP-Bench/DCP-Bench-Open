import sys
import time
from cvc5.pythonic import *

cfg = sys.argv[1]


def run(label, build):
    s = Solver() if cfg == "default" else SolverFor("QF_NIA")
    if cfg == "nlext":
        s = SolverFor("QF_NIA")
        s.set("nl-ext", "full")
    if cfg == "nlext-default-logic":
        s = Solver()
        s.set("nl-ext", "full")
    s.set("tlimit-per", 20000)
    build(s)
    t0 = time.time()
    r = s.check()
    dt = time.time() - t0
    extra = ""
    if r == sat:
        m = s.model()
        extra = "model=" + str(m)
    print(f"{cfg} {label}: {r} reason={s.reason_unknown() if r == unknown else '-'} t={dt:.2f}s {extra}")


a, b, c = Ints("a b c")


def m1(s):
    s.add(a * b == 143, a > 1, b > 1)


def m2(s):
    s.add(a * b * c == 1000, a >= 1, b >= 1, c >= 1, a <= 100, b <= 100, c <= 100)


def m3(s):
    s.add(a * a == 2)


def m4(s):
    s.add(a * a + b * b == 3)


def m5(s):
    s.add(a * b == 1000003 * 999983, a > 1, b > 1)


def m6(s):
    s.add(a * b == 7, a >= 2, b >= 2, a <= 1000, b <= 1000)


run("a*b=143", m1)
run("a*b*c=1000", m2)
run("a*a=2 (no integer root)", m3)
run("a*a+b*b=3", m4)
run("a*b=prime product, large", m5)
run("a*b=7 bounded", m6)
