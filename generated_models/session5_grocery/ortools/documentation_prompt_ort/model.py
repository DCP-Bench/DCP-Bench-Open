from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables
# Prices in cents, assume reasonable range 1 to 711 (since total is 711 cents)
prices = [model.NewIntVar(1, 711, f'price{i}') for i in range(4)]

# Constraints
# Sum of the four items is 711 cents
model.Add(sum(prices) == 711)

# Product of the four items is 71100 000  (7.11 dollars = 711 cents, product in cents^4)
# To avoid overflow and complexity, we use a helper variable for product
# Since product can be very large, we use a trick: 
# We will use a multiplication chain with intermediate variables

# Create intermediate variables for product calculation
p1 = model.NewIntVar(1, 711**2, 'p1')
p2 = model.NewIntVar(1, 711**3, 'p2')
product = model.NewIntVar(1, 711**4, 'product')

model.AddMultiplicationEquality(p1, [prices[0], prices[1]])
model.AddMultiplicationEquality(p2, [p1, prices[2]])
model.AddMultiplicationEquality(product, [p2, prices[3]])

# Product must be 711^4 cents^4
# But the problem states the product of the four prices is also 7.11 dollars
# The problem states "the cashier multiplied the four items instead of adding them; I’ll try again; Hah, with adding them the price still comes to $7.11"
# So the product of the four prices in dollars is 7.11, but prices are in cents
# So product of prices in cents is 7.11 dollars = 711 cents
# But product of four prices in cents is huge, so the problem means the product of the prices in dollars is 7.11
# So prices in dollars: p_i/100
# product in dollars = (p0/100)*(p1/100)*(p2/100)*(p3/100) = 7.11
# => p0 * p1 * p2 * p3 = 7.11 * 100^4 = 7.11 * 100000000 = 711000000

model.Add(product == 711000000)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'prices': [solver.Value(p) for p in prices]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")