# -------------------------------------------------------------
# Google OR-Tools CP-SAT model for
#   min  a  (a >= 2012)
#   s.t. a - b  = p   (p prime)
#        a * b  = n^2 (perfect square)
# -------------------------------------------------------------

from ortools.sat.python import cp_model
import math
import json

# ----------------------------
# Helper: prime generation
# ----------------------------

def sieve_primes(limit):
    """Simple sieve that returns all primes <= limit."""
    sieve = [True] * (limit + 1)
    sieve[0:2] = [False, False]
    for num in range(2, int(math.isqrt(limit)) + 1):
        if sieve[num]:
            step = num
            start = num * num
            sieve[start: limit + 1: step] = [False] * (((limit - start) // step) + 1)
    return [p for p, is_prime in enumerate(sieve) if is_prime]

# ----------------------------
# Model building
# ----------------------------

model = cp_model.CpModel()

# Search range parameters ----------------------------------------------------
LOWER_A = 2012       # a >= 2012 (given)
MAX_X   = 200        # we will search x in [1, MAX_X]; thus a (=x^2) <= MAX_X^2
UPPER_A = MAX_X ** 2

# Decision variables ---------------------------------------------------------
# Fundamental representation: let a = x^2, b = y^2 (proved in analysis).  
# Then n = x * y and p = a - b.

x = model.NewIntVar(1, MAX_X, 'x')  # x > y (will add constraint)
y = model.NewIntVar(1, MAX_X, 'y')

# Squares and products
# a = x * x
# b = y * y
# n = x * y

# Upper bounds for auxiliary variables
MAX_N = MAX_X * MAX_X   # because n = x*y and x,y <= MAX_X

# create variables
a = model.NewIntVar(LOWER_A, UPPER_A, 'a')
b = model.NewIntVar(1, UPPER_A, 'b')
n = model.NewIntVar(1, MAX_N, 'n')

# p must be a prime ----------------------------------------------------------
# Its maximum value is at most a - 1 <= UPPER_A - 1
prime_list = sieve_primes(UPPER_A)
# Filter primes strictly positive (sieve returns that already)
prime_domain = cp_model.Domain.FromValues(prime_list)

p = model.NewIntVarFromDomain(prime_domain, 'p')

# Constraints ----------------------------------------------------------------
model.AddMultiplicationEquality(a, [x, x])         # a = x^2
model.AddMultiplicationEquality(b, [y, y])         # b = y^2
model.AddMultiplicationEquality(n, [x, y])         # n = x*y

model.Add(a - b == p)                              # difference is prime
model.Add(a >= LOWER_A)                            # a lower bound (redundant via domain)
model.Add(x > y)                                   # ensures a > b > 0

# Objective ------------------------------------------------------------------
model.Minimize(a)

# ----------------------------
# Solve
# ----------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {
        'b': solver.Value(b),
        'p': solver.Value(p),
        'a': solver.Value(a),
        'n': solver.Value(n),
    }
    print(json.dumps(result))
else:
    # If for some reason no solution is found in the current bounds, we still
    # need to output valid JSON (problem guarantees a solution within range).
    print(json.dumps({'b': None, 'p': None, 'a': None, 'n': None}))
