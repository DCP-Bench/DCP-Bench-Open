
import cpmpy as cp
import json
import math

# We use the number-theoretic observation:
# If a*b is a perfect square and gcd(a,b)=1 then a and b are perfect squares:
# a = u^2, b = v^2. Then a-b = (u-v)(u+v) is prime, so u-v must be 1.
# Hence u = v+1, a = u^2, b = v^2, p = 2v+1 = 2u-1 (must be prime), n = u*v.
# We search for the smallest a >= 2012.

# Parameters for the search
base = 44              # smallest v we need to consider is 44 (since u >= 45)
maxU = 1000            # upper bound for u (large enough for this problem)

# Precompute arrays for Element constraints to avoid nonlinear (u*u) in the model
vals = [k*k for k in range(base, maxU+1)]          # squares for k = base..maxU
n_vals = [k*(k-1) for k in range(base, maxU+1)]    # n = k*(k-1) for u=k

# Decision variables
u = cp.intvar(45, maxU, name="u")                          # u >= 45 because a = u^2 >= 2012
a = cp.intvar(2012, maxU*maxU, name="a")
b = cp.intvar(1, maxU*maxU, name="b")
n = cp.intvar(1, maxU*(maxU-1), name="n")
p = cp.intvar(2, 2*maxU, name="p")                         # p = 2u-1 upper bounded by 2*maxU

# Model
model = cp.Model()

# Link a, b, n to u via Element (avoids nonlinear multiplication)
# a = u^2  -> index for a is (u - base)
# b = (u-1)^2 -> index for b is (u - base - 1)
model += cp.Element(vals, u - base) == a
model += cp.Element(vals, u - base - 1) == b
model += cp.Element(n_vals, u - base) == n

# p = a - b and a >= 2012 already enforced by domain of 'a'
model += p == a - b
model += p >= 2

# Primality: ensure no divisor d in 2..sqrt(max_p) divides p
max_p = 2*maxU - 1
max_check = int(math.isqrt(max_p))
for d in range(2, max_check + 1):
    model += (p % d) != 0

# Ensure u-v = 1 implicitly via the Element indexing (b uses u-1 index)
# Minimize a to get the smallest a >= 2012
model.minimize(a)

if model.solve():
    solution = {
        'a': int(a.value()),
        'b': int(b.value()),
        'n': int(n.value()),
        'p': int(p.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
