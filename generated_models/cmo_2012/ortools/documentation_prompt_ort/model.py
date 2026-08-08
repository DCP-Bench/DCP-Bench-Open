from ortools.sat.python import cp_model
import json
import math

# Model definition
model = cp_model.CpModel()

# Since a >= 2012 and a, b are positive integers,
# and a - b = p (prime), and a*b = n^2 (perfect square),
# we need to find smallest a >= 2012 satisfying these.

# We will set an upper bound for search.
# Since a*b = n^2, and a-b = p (prime), b = a - p.
# So a*(a-p) = n^2.
# For a starting at 2012, we try increasing a and p (prime) to find solution.

# To model this in CP-SAT, we need to fix some bounds.
# Let's set upper bound for a as 10000 (arbitrary large enough).
# p is prime and less than a (since b = a - p > 0).
# n can be up to sqrt(a*b) <= a (since b < a).

MAX_A = 10000
MIN_A = 2012

# Decision variables
a = model.NewIntVar(MIN_A, MAX_A, 'a')
p = model.NewIntVar(2, MAX_A, 'p')  # p is prime, at least 2
b = model.NewIntVar(1, MAX_A, 'b')
n = model.NewIntVar(1, MAX_A * MAX_A, 'n')  # n^2 = a*b, n can be large

# Constraints
model.Add(b == a - p)
model.Add(b > 0)

# a*b = n^2
# We cannot directly model multiplication and perfect square easily in CP-SAT,
# but we can use a trick: n^2 = a*b
# We can use a table or a custom constraint.
# However, CP-SAT does not support nonlinear constraints directly.
# So we will use a search approach with a callback.

# Instead, we will implement a custom search outside CP-SAT,
# because CP-SAT is not suitable for nonlinear constraints like perfect squares.

# So we will implement a direct search for the smallest a >= 2012.

def is_prime(x):
    if x < 2:
        return False
    if x == 2:
        return True
    if x % 2 == 0:
        return False
    r = int(math.isqrt(x))
    for i in range(3, r + 1, 2):
        if x % i == 0:
            return False
    return True

def is_perfect_square(x):
    r = int(math.isqrt(x))
    return r * r == x

# Search for smallest a >= 2012
found = False
for a_val in range(MIN_A, MAX_A + 1):
    # p must be prime and less than a_val
    # b = a_val - p > 0
    # So p < a_val
    # We try all primes p < a_val
    # To optimize, p must be less than a_val and positive
    # Also, a_val * b = n^2
    # So check for each prime p if a_val*(a_val - p) is perfect square
    for p_val in range(2, a_val):
        if is_prime(p_val):
            b_val = a_val - p_val
            if b_val <= 0:
                continue
            product = a_val * b_val
            if is_perfect_square(product):
                n_val = int(math.isqrt(product))
                # Found solution
                solution = {
                    'a': a_val,
                    'b': b_val,
                    'n': n_val,
                    'p': p_val
                }
                print(json.dumps(solution, indent=4))
                found = True
                break
    if found:
        break

if not found:
    print("No solution found.")