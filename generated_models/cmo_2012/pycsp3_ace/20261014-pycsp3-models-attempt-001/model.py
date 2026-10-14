from pycsp3 import *

min_a = data.min_a
max_val = data.max_val

primes = [p for p in range(2, max_val + 1) if all(p % q != 0 for q in range(2, int(p ** 0.5) + 1))]

# a and b are positive integers, a at most the bound. Both are perfect squares:
# with a*b = n^2 and a-b prime, a = u^2 and b = v^2 with u = v+1 (the square-free parts cancel).
squares = [u * u for u in range(1, max_val + 1) if u * u <= max_val]
a = Var(dom=[s for s in squares if s >= min_a])
b = Var(dom=squares)
n = Var(dom=range(1, max_val + 1))
p = Var(dom=primes)

satisfy(
    # the difference of a and b is a prime number
    a - b == p,
    # the product of a and b is a perfect square n^2
    a * b == n * n,
)

# the smallest value of a is wanted
minimize(a)
