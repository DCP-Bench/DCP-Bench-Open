import bitwuzla as bz
import json

tm = bz.TermManager()
options = bz.Options()
options.set(bz.Option.PRODUCE_MODELS, True)
solver = bz.Bitwuzla(tm, options)
sort = tm.mk_bv_sort(16)

# Decision variables: number of men, women, and children (8-bit values in 16-bit registers)
men = tm.mk_const(sort, "men")
women = tm.mk_const(sort, "women")
children = tm.mk_const(sort, "children")


def bv(n):
    return tm.mk_bv_value(sort, n)


def ule(a, b):
    return tm.mk_term(bz.Kind.BV_ULE, [a, b])


def eq(a, b):
    return tm.mk_term(bz.Kind.EQUAL, [a, b])


def add(*args):
    term = args[0]
    for arg in args[1:]:
        term = tm.mk_term(bz.Kind.BV_ADD, [term, arg])
    return term


def mul(a, b):
    return tm.mk_term(bz.Kind.BV_MUL, [a, b])


solver.assert_formula(ule(men, bv(100)))
solver.assert_formula(ule(women, bv(100)))
solver.assert_formula(ule(children, bv(100)))
# 100 people in total
solver.assert_formula(eq(add(men, women, children), bv(100)))
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
solver.assert_formula(eq(add(mul(bv(6), men), mul(bv(4), women), children), bv(200)))
# Five times as many women as men
solver.assert_formula(eq(women, mul(bv(5), men)))

if solver.check_sat() != bz.Result.SAT:
    raise SystemExit("No solution found.")


def as_int(term):
    return int(solver.get_value(term).value(10))


print(json.dumps({
    "men": as_int(men),
    "women": as_int(women),
    "children": as_int(children),
}))
