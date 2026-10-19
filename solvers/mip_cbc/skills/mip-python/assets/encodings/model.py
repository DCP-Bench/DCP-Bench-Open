# Linear encodings of constraints that are not linear at first sight: not-equal, absolute value,
# min and max, product of two binaries, product of a binary and an integer, strict inequality on
# integers, and a flag that is 1 exactly when a value reaches a threshold.
# Each block builds its own small model and prints one answer line.
import mip

S = dict(solver_name="CBC")


def new_model(sense=mip.MINIMIZE):
    m = mip.Model(sense=sense, **S)
    m.verbose = 0
    m.max_mip_gap = 0.0
    m.max_mip_gap_abs = 0.0
    return m


# not-equal: x != 5 for x in 0..5, maximise x.
# Binary b selects the side: b = 0 gives x <= 4, b = 1 gives x >= 6 (only reachable if the upper
# bound allows it). M = 1 + (hi - v) on the first and M = v + 1 - lo on the second, both from the bounds.
m = new_model(mip.MAXIMIZE)
x = m.add_var("x", lb=0, ub=5, var_type=mip.INTEGER)
v, lo, hi = 5, 0, 5
b = m.add_var("b", var_type=mip.BINARY)
m += x <= v - 1 + (hi - v + 1) * b
m += x >= v + 1 - (v + 1 - lo) * (1 - b)
m.objective = x
m.optimize(max_seconds=30)
print("x != 5: max x =", round(x.x))

# absolute value: d = |a - b| with a + b = 9, minimise d. Minimising, d >= a - b and d >= b - a suffice.
m = new_model()
a = m.add_var("a", lb=0, ub=9, var_type=mip.INTEGER)
bb = m.add_var("bb", lb=0, ub=9, var_type=mip.INTEGER)
d = m.add_var("d", lb=0, ub=9, var_type=mip.INTEGER)
m += a + bb == 9
m += d >= a - bb
m += d >= bb - a
m.objective = d
m.optimize(max_seconds=30)
print("abs: min |a-b| =", round(d.x))

# min and max: maximise the smaller of x and y (m <= x, m <= y), and minimise the larger (M >= x, M >= y)
m = new_model(mip.MAXIMIZE)
x = m.add_var("x", lb=0, ub=9, var_type=mip.INTEGER)
y = m.add_var("y", lb=0, ub=9, var_type=mip.INTEGER)
lower = m.add_var("lower", lb=0, ub=9, var_type=mip.INTEGER)
m += x + y <= 9
m += lower <= x
m += lower <= y
m.objective = lower
m.optimize(max_seconds=30)
best_min = round(lower.x)

m = new_model()
x = m.add_var("x", lb=0, ub=9, var_type=mip.INTEGER)
y = m.add_var("y", lb=0, ub=9, var_type=mip.INTEGER)
upper = m.add_var("upper", lb=0, ub=9, var_type=mip.INTEGER)
m += x + y >= 9
m += upper >= x
m += upper >= y
m.objective = upper
m.optimize(max_seconds=30)
print("min/max: max min(x,y) =", best_min, ", min max(x,y) =", round(upper.x))

# product of two binaries: z = p * q, with p and q fixed to 1 and 1 by the constraints below
m = new_model()
p = m.add_var("p", var_type=mip.BINARY)
q = m.add_var("q", var_type=mip.BINARY)
z = m.add_var("z", var_type=mip.BINARY)
m += z <= p
m += z <= q
m += z >= p + q - 1
m += p == 1
m += q >= 1
m.objective = z
m.optimize(max_seconds=30)
print("product of binaries: z =", round(z.x))

# product of a binary and an integer: w = b * x for x in 0..9, with b = 1 and x = 7 forced
m = new_model()
b = m.add_var("b", var_type=mip.BINARY)
x = m.add_var("x", lb=0, ub=9, var_type=mip.INTEGER)
w = m.add_var("w", lb=0, ub=9, var_type=mip.INTEGER)
lo, hi = 0, 9
m += w <= hi * b
m += w >= lo * b
m += w <= x - lo * (1 - b)
m += w >= x - hi * (1 - b)
m += b == 1
m += x == 7
m.objective = w
m.optimize(max_seconds=30)
print("product of binary and integer: w =", round(w.x))

# strict inequality on integers: 3 < x < 6 is 4 <= x <= 5, so write the bounds with +1 and -1
m = new_model(mip.MAXIMIZE)
x = m.add_var("x", lb=0, ub=9, var_type=mip.INTEGER)
m += x >= 3 + 1
m += x <= 6 - 1
m.objective = x
m.optimize(max_seconds=30)
print("strict: x =", round(x.x))

# flag c is 1 exactly when x >= 3, for x in 0..5. Lower M = 3 - lo, upper M = hi - 2 (both from bounds).
m = new_model()
x = m.add_var("x", lb=0, ub=5, var_type=mip.INTEGER)
c = m.add_var("c", var_type=mip.BINARY)
m += x >= 3 - 3 * (1 - c)
m += x <= 2 + 3 * c
m += x == 4
m.objective = c
m.optimize(max_seconds=30)
print("flag =", round(c.x))
