from cpmpy import *
import json

# Decision variables
# x[i] = 1 if investment i is chosen, 0 otherwise
x = boolvar(shape=4, name="x")

# NPV and cash outflow for each investment (in thousands of dollars)
npv = [16, 22, 12, 8]
cash_outflow = [5, 7, 4, 3]
available_cash = 14

# Model
model = Model()

# Objective: maximize the total NPV
total_npv = sum([npv[i] * x[i] for i in range(4)])
model.maximize(total_npv)

# Constraint: total cash outflow must not exceed available cash
model += [sum([cash_outflow[i] * x[i] for i in range(4)]) <= available_cash]

# Solve the model
model.solve()

# Print the solution
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))