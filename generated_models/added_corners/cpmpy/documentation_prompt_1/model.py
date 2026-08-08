
import cpmpy as cp
import json

# Positions:
# C = circle, F = square
# Layout:
#   C F C
#   F   F
#   C F C
#
# Let's name variables as follows:
# Circles: c1, c2, c3, c4 (top-left, top-right, bottom-left, bottom-right)
# Squares: f1, f2, f3, f4, f5 (top-middle, middle-left, middle-right, bottom-middle, center)
#
# Adjacencies (square = sum of adjoining circles):
# f1 = c1 + c2
# f2 = c1 + c3
# f3 = c2 + c4
# f4 = c3 + c4
# f5 = c1 + c2 + c3 + c4 (center square)

model = cp.Model()

# Decision variables: digits 1..8, all distinct
c = cp.intvar(1, 8, shape=4, name="c")  # circles: c[0]=c1, c[1]=c2, c[2]=c3, c[3]=c4
f = cp.intvar(1, 8, shape=5, name="f")  # squares: f[0]=f1, f[1]=f2, f[2]=f3, f[3]=f4, f[4]=f5

# All digits 1..8 used exactly once
model += cp.AllDifferent(c.tolist() + f.tolist())

# Constraints for squares equal to sum of adjoining circles
model += (f[0] == c[0] + c[1])  # f1 = c1 + c2
model += (f[1] == c[0] + c[2])  # f2 = c1 + c3
model += (f[2] == c[1] + c[3])  # f3 = c2 + c4
model += (f[3] == c[2] + c[3])  # f4 = c3 + c4
model += (f[4] == c[0] + c[1] + c[2] + c[3])  # f5 = c1 + c2 + c3 + c4

if model.solve():
    positions = {
        "c1": int(c[0].value()),
        "f1": int(f[0].value()),
        "c2": int(c[1].value()),
        "f2": int(f[1].value()),
        "f5": int(f[4].value()),
        "f3": int(f[2].value()),
        "c3": int(c[2].value()),
        "f4": int(f[3].value()),
        "c4": int(c[3].value())
    }
    print(json.dumps({"positions": positions}, indent=4))
else:
    print("No solution found.")
