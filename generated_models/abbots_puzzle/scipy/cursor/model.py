from scipy.optimize import Bounds, LinearConstraint, milp
import json
import numpy as np

# x = [men, women, children]
c = np.zeros(3)
bounds = Bounds(0, 100)
constraints = LinearConstraint(
    np.array([
        [1, 1, 1],
        [6, 4, 1],
        [-5, 1, 0],
    ], dtype=float),
    lb=np.array([100.0, 200.0, 0.0]),
    ub=np.array([100.0, 200.0, 0.0]),
)
result = milp(c, integrality=np.ones(3), bounds=bounds, constraints=constraints)
if result.x is None:
    raise SystemExit(f"No solution found ({result.message}).")

print(json.dumps({
    "men": int(round(result.x[0])),
    "women": int(round(result.x[1])),
    "children": int(round(result.x[2])),
}))
