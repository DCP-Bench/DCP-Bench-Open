from cylp.cy import CyClpSimplex
from cylp.py.modeling.CyLPModel import CyLPModel
import json

model = CyLPModel()
# Decision variables: number of men, women, and children
x = model.addVariable("x", 3, isInt=True)
model += 0 <= x
model += x <= 100
# 100 people in total
model += x[0] + x[1] + x[2] == 100
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
model += 6 * x[0] + 4 * x[1] + x[2] == 200
# Five times as many women as men
model += x[1] - 5 * x[0] == 0

simplex = CyClpSimplex(model)
cbc = simplex.getCbcModel()
cbc.logLevel = 0
status = cbc.solve()
sol = cbc.primalVariableSolution.get("x")
if sol is None:
    raise SystemExit(f"No solution found ({status}).")

print(json.dumps({
    "men": int(round(sol[0])),
    "women": int(round(sol[1])),
    "children": int(round(sol[2])),
}))
