from cvxopt import glpk, matrix
import json
import numpy as np

# x = [men, women, children]; bounds 0 <= x <= 100 as Gx <= h
c = matrix([0.0, 0.0, 0.0])
G = matrix(np.vstack([-np.eye(3), np.eye(3)]))
h = matrix([0.0, 0.0, 0.0, 100.0, 100.0, 100.0])
A = matrix(np.array([
    [1.0, 1.0, 1.0],
    [6.0, 4.0, 1.0],
    [-5.0, 1.0, 0.0],
], dtype=float))
b = matrix([100.0, 200.0, 0.0])

status, x = glpk.ilp(c, G, h, A, b, I=set([0, 1, 2]))
if x is None:
    raise SystemExit(f"No solution found ({status}).")

print(json.dumps({
    "men": int(round(x[0])),
    "women": int(round(x[1])),
    "children": int(round(x[2])),
}))
