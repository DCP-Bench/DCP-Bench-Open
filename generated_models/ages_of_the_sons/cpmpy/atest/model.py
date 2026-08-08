from cpmpy import *
import json

# Decision variables
A1 = intvar(1, 36, name="A1")  # Oldest son's age
A2 = intvar(1, 36, name="A2")  # Middle son's age
A3 = intvar(1, 36, name="A3")  # Youngest son's age

# Model
model = Model()

# Product of their ages is 36
model += [A1 * A2 * A3 == 36]

# All ages are positive integers and ordered from oldest to youngest
model += [A1 >= A2, A2 >= A3]

# There is a unique oldest son (i.e., A1 > A2)
model += [A1 > A2]

# Collect all possible combinations of (A1, A2, A3) that satisfy the above constraints
possible_solutions = []
for sol in model.enumerate(solver="ortools", time_limit=10):
    possible_solutions.append((sol[A1], sol[A2], sol[A3]))

# Find the solution where the sum is ambiguous (i.e., appears more than once)
sum_counts = {}
for sol in possible_solutions:
    s = sum(sol)
    if s in sum_counts:
        sum_counts[s].append(sol)
    else:
        sum_counts[s] = [sol]

# Find the sum that has multiple solutions
ambiguous_sum = None
for s, solutions in sum_counts.items():
    if len(solutions) > 1:
        ambiguous_sum = s
        break

# Among the solutions with the ambiguous sum, find the one with a unique oldest son
for sol in sum_counts[ambiguous_sum]:
    if sol[0] > sol[1] and sol[1] == sol[2]:
        A1_val, A2_val, A3_val = sol
        break

# Print the solution
solution = {"A3": A3_val, "A1": A1_val, "A2": A2_val}
print(json.dumps(solution))