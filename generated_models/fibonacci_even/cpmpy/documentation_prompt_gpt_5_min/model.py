
import cpmpy as cp
import json

# Data
MAXV = 4_000_000
N = 33  # enough terms so that the last term <= MAXV (F1=1, F2=2, ..., F32=3524578 <= 4M)

# Model definition
model = cp.Model()

# Decision Variables
# Fibonacci numbers (indexed 0..N-1 corresponding to F1..FN)
fib = cp.intvar(0, 6_000_000, shape=N, name="fib")  # upper bound > largest Fibonacci we may encounter
take = cp.boolvar(shape=N, name="take")            # whether fib[i] <= MAXV
is_even = cp.boolvar(shape=N, name="is_even")      # whether fib[i] is even
contrib = cp.boolvar(shape=N, name="contrib")      # take[i] and is_even[i]
res = cp.intvar(0, 10_000_000, name="res")         # sum of even-valued terms <= 10M to be safe

# Constraints
# Starting values
model += (fib[0] == 1)
model += (fib[1] == 2)

# Fibonacci recurrence
for i in range(2, N):
    model += (fib[i] == fib[i-1] + fib[i-2])

# Link booleans and contribution
for i in range(N):
    model += (take[i] == (fib[i] <= MAXV))
    model += (is_even[i] == (fib[i] % 2 == 0))
    model += (contrib[i] == (take[i] & is_even[i]))

# Define result as the sum of even Fibonacci numbers not exceeding MAXV
model += (res == cp.sum([contrib[i] * fib[i] for i in range(N)]))

# Solve and print
if model.solve():
    solution = {'res': int(res.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
