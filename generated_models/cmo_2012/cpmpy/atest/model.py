from cpmpy import *
import json

# Decision variables
a = intvar(2012, 10000, name="a")  # a is at least 2012
b = intvar(1, 10000, name="b")
n = intvar(0, 10000, name="n")
p = intvar(1, 10000, name="p")

# Model
model = Model()

# a - b is a prime number p
model += [a - b == p]

# a * b is a perfect square n^2
model += [a * b == n * n]

# p is a prime number
# A prime number is greater than 1 and has no divisors other than 1 and itself
model += [p > 1]

# Define a helper variable for checking primality
d = intvar(2, 10000, name="d")
model += [d <= p // 2]  # Limit d to be at most half of p
model += [p % d != 0]  # p must not be divisible by d

# Ensure that for all d in 2 to p-1, p % d != 0
# This is a simplified approach for CPMPy
model += [forall([d], p % d != 0)]

# Objective: minimize a
model.minimize(a)

# Solve the model
model.solve()

# Print the solution
solution = {
    "a": a.value(),
    "b": b.value(),
    "n": n.value(),
    "p": p.value()
}
print(json.dumps(solution))