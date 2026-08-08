from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables: quantities of each fruit
# Since we want to minimize bananas and apples but still buy at least one of each fruit,
# we set the lower bound to 1 for bananas and apples.
bananas = model.NewIntVar(1, 100, 'bananas')
oranges = model.NewIntVar(1, 100, 'oranges')
mangoes = model.NewIntVar(1, 100, 'mangoes')
apples = model.NewIntVar(1, 100, 'apples')

# Constraints

# Total fruits must be 100
model.Add(bananas + oranges + mangoes + apples == 100)

# Total cost must be 100 dollars
# Cost per fruit:
# 3 dollars for 5 bananas => 3/5 dollars per banana
# 5 dollars for 7 oranges => 5/7 dollars per orange
# 7 dollars for 9 mangoes => 7/9 dollars per mango
# 9 dollars for 3 apples => 9/3 = 3 dollars per apple
# To avoid floating point, multiply all costs by 63 (LCM of denominators 5,7,9,1)
# bananas cost: 3/5 * 63 = 3*63/5 = 37.8 -> 38 (approx)
# oranges cost: 5/7 * 63 = 5*63/7 = 45
# mangoes cost: 7/9 * 63 = 7*63/9 = 49
# apples cost: 3 * 63 = 189
# We'll use exact fractions by multiplying quantities accordingly.

# Let's multiply quantities by their cost numerator and divide by denominator:
# To keep integer arithmetic, we can multiply the entire cost equation by 315 (LCM of 5,7,9,1)
# 315/5 = 63, 315/7=45, 315/9=35, 315/1=315
# So cost equation:
# bananas * 3 * 63 + oranges * 5 * 45 + mangoes * 7 * 35 + apples * 3 * 315 = 100 * 315
# Simplify:
# bananas * 189 + oranges * 225 + mangoes * 245 + apples * 945 = 31500

model.Add(bananas * 189 + oranges * 225 + mangoes * 245 + apples * 945 == 31500)

# Objective: minimize bananas + apples (since user dislikes these)
model.Minimize(bananas + apples)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'bananas': solver.Value(bananas),
        'oranges': solver.Value(oranges),
        'mangoes': solver.Value(mangoes),
        'apples': solver.Value(apples)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")