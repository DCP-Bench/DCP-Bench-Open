# Import libraries
from cpmpy import *
import json

# Parameters
npv = [16000, 22000, 12000, 8000]  # Net present values of investments
cost = [5000, 7000, 4000, 3000]    # Cash outflows for investments
budget = 14000                      # Available budget
n_investments = len(npv)            # Number of investments

# Decision Variables
x = boolvar(shape=n_investments, name="x")  # Whether each investment is chosen (True/False)

# Model
model = Model()

# Constraint: total cost does not exceed budget
model += sum(x[i] * cost[i] for i in range(n_investments)) <= budget

# Objective: maximize total NPV
model.maximize(sum(x[i] * npv[i] for i in range(n_investments)))

# Solve
model.solve()

# Print solution
solution = {
    "z": sum(x[i].value() * npv[i] for i in range(n_investments)),
    "x": [bool(val) for val in x.value()]
}
print(json.dumps(solution))
# End of CPMPy script