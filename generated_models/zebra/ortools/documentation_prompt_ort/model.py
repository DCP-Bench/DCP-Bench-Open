from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

houses = range(1, 6)  # Houses numbered 1 to 5 from left to right

# Define variables for each attribute: color, nation, pet, drink, job
colors = ['yellow', 'green', 'red', 'white', 'blue']
nations = ['italy', 'spain', 'japan', 'england', 'norway']
pets = ['cat', 'zebra', 'bear', 'snails', 'horse']
drinks = ['milk', 'water', 'tea', 'coffee', 'juice']
jobs = ['painter', 'sculptor', 'diplomat', 'pianist', 'doctor']

# Create variables for each attribute value representing the house number
color_vars = {c: model.NewIntVar(1, 5, c) for c in colors}
nation_vars = {n: model.NewIntVar(1, 5, n) for n in nations}
pet_vars = {p: model.NewIntVar(1, 5, p) for p in pets}
drink_vars = {d: model.NewIntVar(1, 5, d) for d in drinks}
job_vars = {j: model.NewIntVar(1, 5, j) for j in jobs}

# All different constraints for each attribute group
model.AddAllDifferent(color_vars.values())
model.AddAllDifferent(nation_vars.values())
model.AddAllDifferent(pet_vars.values())
model.AddAllDifferent(drink_vars.values())
model.AddAllDifferent(job_vars.values())

# Constraints from the puzzle

# The painter owns the horse
model.Add(job_vars['painter'] == pet_vars['horse'])

# The diplomat drinks coffee
model.Add(job_vars['diplomat'] == drink_vars['coffee'])

# The one who drinks milk lives in the white house
model.Add(drink_vars['milk'] == color_vars['white'])

# The Spaniard is a painter
model.Add(nation_vars['spain'] == job_vars['painter'])

# The Englishman lives in the red house
model.Add(nation_vars['england'] == color_vars['red'])

# The snails are owned by the sculptor
model.Add(pet_vars['snails'] == job_vars['sculptor'])

# The green house is on the left of the red one (immediately to the left)
model.Add(color_vars['green'] + 1 == color_vars['red'])

# The Norwegian lives on the right of the blue house (immediately to the right)
model.Add(nation_vars['norway'] == color_vars['blue'] + 1)

# The doctor drinks milk
model.Add(job_vars['doctor'] == drink_vars['milk'])

# The diplomat is Japanese
model.Add(job_vars['diplomat'] == nation_vars['japan'])

# The Norwegian owns the zebra
model.Add(nation_vars['norway'] == pet_vars['zebra'])

# The green house is next to the white one (adjacent houses)
model.AddAbsEquality(model.NewIntVar(1, 4, 'green_white_diff'),
                     color_vars['green'] - color_vars['white'])
model.AddAbsEquality(model.NewIntVar(1, 4, 'green_white_diff2'),
                     color_vars['green'] - color_vars['white'])
model.Add((color_vars['green'] - color_vars['white']).Abs() == 1)

# The horse is owned by the neighbor of the diplomat (adjacent houses)
model.AddAbsEquality(model.NewIntVar(1, 4, 'horse_diplomat_diff'),
                     pet_vars['horse'] - job_vars['diplomat'])
model.Add((pet_vars['horse'] - job_vars['diplomat']).Abs() == 1)

# The Italian either lives in the red, white or green house
# So Italian's house is in {red, white, green}
# We model this as: Italian's house == red or white or green
italian_house = nation_vars['italy']
red_house = color_vars['red']
white_house = color_vars['white']
green_house = color_vars['green']

# Create boolean variables for the three possibilities
italy_red = model.NewBoolVar('italy_red')
italy_white = model.NewBoolVar('italy_white')
italy_green = model.NewBoolVar('italy_green')

model.Add(italian_house == red_house).OnlyEnforceIf(italy_red)
model.Add(italian_house != red_house).OnlyEnforceIf(italy_red.Not())

model.Add(italian_house == white_house).OnlyEnforceIf(italy_white)
model.Add(italian_house != white_house).OnlyEnforceIf(italy_white.Not())

model.Add(italian_house == green_house).OnlyEnforceIf(italy_green)
model.Add(italian_house != green_house).OnlyEnforceIf(italy_green.Not())

model.AddBoolOr([italy_red, italy_white, italy_green])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'colors': [solver.Value(color_vars[c]) for c in colors],
        'nations': [solver.Value(nation_vars[n]) for n in nations],
        'jobs': [solver.Value(job_vars[j]) for j in jobs],
        'pets': [solver.Value(pet_vars[p]) for p in pets],
        'drinks': [solver.Value(drink_vars[d]) for d in drinks]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")