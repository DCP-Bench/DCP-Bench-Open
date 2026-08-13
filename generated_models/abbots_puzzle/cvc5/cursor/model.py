from cvc5 import Solver, Kind
import json

solver = Solver()
solver.setLogic("QF_LIA")
solver.setOption("produce-models", "true")
int_sort = solver.getIntegerSort()

# Decision variables: number of men, women, and children
men = solver.mkConst(int_sort, "men")
women = solver.mkConst(int_sort, "women")
children = solver.mkConst(int_sort, "children")


def iconst(n):
    return solver.mkInteger(n)


solver.assertFormula(solver.mkTerm(Kind.GEQ, men, iconst(0)))
solver.assertFormula(solver.mkTerm(Kind.LEQ, men, iconst(100)))
solver.assertFormula(solver.mkTerm(Kind.GEQ, women, iconst(0)))
solver.assertFormula(solver.mkTerm(Kind.LEQ, women, iconst(100)))
solver.assertFormula(solver.mkTerm(Kind.GEQ, children, iconst(0)))
solver.assertFormula(solver.mkTerm(Kind.LEQ, children, iconst(100)))

# 100 people in total
solver.assertFormula(solver.mkTerm(Kind.EQUAL, solver.mkTerm(Kind.ADD, men, women, children), iconst(100)))
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
solver.assertFormula(solver.mkTerm(
    Kind.EQUAL,
    solver.mkTerm(Kind.ADD, solver.mkTerm(Kind.MULT, iconst(6), men),
                  solver.mkTerm(Kind.MULT, iconst(4), women), children),
    iconst(200),
))
# Five times as many women as men
solver.assertFormula(solver.mkTerm(Kind.EQUAL, women, solver.mkTerm(Kind.MULT, iconst(5), men)))

if not solver.checkSat().isSat():
    raise SystemExit("No solution found.")

print(json.dumps({
    "men": int(solver.getValue(men).getIntegerValue()),
    "women": int(solver.getValue(women).getIntegerValue()),
    "children": int(solver.getValue(children).getIntegerValue()),
}))
