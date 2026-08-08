
import cpmpy as cp
import json
import math

# We want to find positive integers a, b, n, p such that:
# 1) a - b = p, where p is prime
# 2) a * b = n^2 (a perfect square)
# 3) a >= 2012
# We want to minimize a.

# To model this, we need to consider the domain of variables.
# Since a >= 2012, let's set an upper bound for a to search for a solution.
# We can try a reasonable upper bound, say 3000, to keep the problem solvable.

# We will generate primes up to the upper bound difference (a-b).
# The difference p = a - b must be prime and positive.
# Also, a and b are positive integers.

# Let's define the upper bound for a and b
a_min = 2012
a_max = 3000

# The difference p = a - b must be positive prime, so p < a_max
# We'll generate primes up to a_max for p.

def sieve_primes(n):
    sieve = [True]*(n+1)
    sieve[0] = False
    sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

primes = sieve_primes(a_max)

model = cp.Model()

# Decision variables
# a, b, n, p
a = cp.intvar(a_min, a_max, name="a")
b = cp.intvar(1, a_max, name="b")  # b positive integer, less than or equal to a_max
n = cp.intvar(1, a_max, name="n")  # n positive integer, n^2 = a*b
p = cp.intvar(2, a_max, name="p")  # p prime difference

# Constraints
model += (a - b == p)
model += (a * b == n * n)
model += (p > 0)

# p must be prime, so p in primes
# We use a table constraint to restrict p to primes
model += cp.Table([p], [[pr] for pr in primes])

# b must be positive and less than or equal to a
model += (b <= a)

# Objective: minimize a
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
