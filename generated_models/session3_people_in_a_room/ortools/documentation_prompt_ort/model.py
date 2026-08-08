from ortools.sat.python import cp_model
import json

# Number of people
total_people = 13
males = 4
females = total_people - males

# Model definition
model = cp_model.CpModel()

# Decision Variables
# sequence[i] = 0 if male enters at position i, 1 if female enters at position i
sequence = [model.NewIntVar(0, 1, f'seq_{i}') for i in range(total_people)]

# Constraints
# Exactly 4 males and 9 females in the sequence
model.Add(sum(sequence) == females)  # sum of females = 9
model.Add(sum(sequence[i] == 0 for i in range(total_people)) == males)  # sum of males = 4
# The above line is not valid syntax, so we use:
model.Add(sum(sequence[i].Not() for i in range(total_people)) == males)  # males count

# Prefix sums for females and males
prefix_females = []
prefix_males = []
females_sum = 0
males_sum = 0
for i in range(total_people):
    # Create prefix sum variables
    pf = model.NewIntVar(0, females, f'prefix_females_{i}')
    pm = model.NewIntVar(0, males, f'prefix_males_{i}')
    prefix_females.append(pf)
    prefix_males.append(pm)

# Define prefix sums
for i in range(total_people):
    if i == 0:
        model.Add(prefix_females[i] == sequence[i])
        # males = 1 - sequence[i]
        model.Add(prefix_males[i] == 1 - sequence[i])
    else:
        model.Add(prefix_females[i] == prefix_females[i-1] + sequence[i])
        model.Add(prefix_males[i] == prefix_males[i-1] + (1 - sequence[i]))

# Ratio constraint: females/males <= 7/3 at any time
# For each prefix i, if males > 0, then females * 3 <= males * 7
# If males == 0, then females must be 0 (to avoid division by zero and ratio > 7/3)
for i in range(total_people):
    # Create boolean variable males_positive
    males_positive = model.NewBoolVar(f'males_positive_{i}')
    model.Add(prefix_males[i] > 0).OnlyEnforceIf(males_positive)
    model.Add(prefix_males[i] == 0).OnlyEnforceIf(males_positive.Not())

    # females * 3 <= males * 7 when males > 0
    # Use a big-M constraint to enforce this only when males_positive is true
    # big M can be total_people * 7 (max possible)
    big_M = total_people * 7
    model.Add(prefix_females[i] * 3 <= prefix_males[i] * 7).OnlyEnforceIf(males_positive)

    # If males == 0, females must be 0
    model.Add(prefix_females[i] == 0).OnlyEnforceIf(males_positive.Not())

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'sequence': [solver.Value(sequence[i]) for i in range(total_people)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")