from pyomo.environ import ConcreteModel, Constraint, NonNegativeIntegers, Var, value
from pyomo.contrib.appsi.solvers import Highs
import json

m = ConcreteModel()
# Decision variables: number of men, women, and children
m.men = Var(domain=NonNegativeIntegers, bounds=(0, 100))
m.women = Var(domain=NonNegativeIntegers, bounds=(0, 100))
m.children = Var(domain=NonNegativeIntegers, bounds=(0, 100))

# 100 people in total
m.people = Constraint(expr=m.men + m.women + m.children == 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
m.bushels = Constraint(expr=6 * m.men + 4 * m.women + m.children == 200)
# Five times as many women as men
m.ratio = Constraint(expr=m.women == 5 * m.men)

opt = Highs()
opt.highs_options["output_flag"] = False
result = opt.solve(m)
term = str(result.termination_condition)
if value(m.men) is None:
    raise SystemExit(f"No solution found ({term}).")

print(json.dumps({
    "men": int(round(value(m.men))),
    "women": int(round(value(m.women))),
    "children": int(round(value(m.children))),
}))
