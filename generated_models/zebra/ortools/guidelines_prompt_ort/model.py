
from ortools.sat.python import cp_model
import json

# Create the model
model = cp_model.CpModel()

# There are 5 houses numbered 1 to 5
hmin, hmax = 1, 5

# Decision variables for each attribute: the house number for each item
# Colors
yellow = model.NewIntVar(hmin, hmax, 'yellow')
green = model.NewIntVar(hmin, hmax, 'green')
red = model.NewIntVar(hmin, hmax, 'red')
white = model.NewIntVar(hmin, hmax, 'white')
blue = model.NewIntVar(hmin, hmax, 'blue')

# Nations
italy = model.NewIntVar(hmin, hmax, 'italy')
spain = model.NewIntVar(hmin, hmax, 'spain')
japan = model.NewIntVar(hmin, hmax, 'japan')
england = model.NewIntVar(hmin, hmax, 'england')
norway = model.NewIntVar(hmin, hmax, 'norway')

# Pets
cat = model.NewIntVar(hmin, hmax, 'cat')
zebra = model.NewIntVar(hmin, hmax, 'zebra')
bear = model.NewIntVar(hmin, hmax, 'bear')
snails = model.NewIntVar(hmin, hmax, 'snails')
horse = model.NewIntVar(hmin, hmax, 'horse')

# Drinks
milk = model.NewIntVar(hmin, hmax, 'milk')
water = model.NewIntVar(hmin, hmax, 'water')
tea = model.NewIntVar(hmin, hmax, 'tea')
coffee = model.NewIntVar(hmin, hmax, 'coffee')
juice = model.NewIntVar(hmin, hmax, 'juice')

# Jobs
painter = model.NewIntVar(hmin, hmax, 'painter')
sculptor = model.NewIntVar(hmin, hmax, 'sculptor')
diplomat = model.NewIntVar(hmin, hmax, 'diplomat')
pianist = model.NewIntVar(hmin, hmax, 'pianist')
doctor = model.NewIntVar(hmin, hmax, 'doctor')

# All-different constraints for each category
model.AddAllDifferent([yellow, green, red, white, blue])
model.AddAllDifferent([italy, spain, japan, england, norway])
model.AddAllDifferent([cat, zebra, bear, snails, horse])
model.AddAllDifferent([milk, water, tea, coffee, juice])
model.AddAllDifferent([painter, sculptor, diplomat, pianist, doctor])

# Clues as constraints:

# The painter owns the horse
model.Add(painter == horse)

# The diplomat drinks coffee
model.Add(diplomat == coffee)

# The one who drinks milk lives in the white house
model.Add(milk == white)

# The Spaniard is a painter
model.Add(spain == painter)

# The Englishman lives in the red house
model.Add(england == red)

# The snails are owned by the sculptor
model.Add(snails == sculptor)

# The green house is on the left of the red one (somewhere to the left)
model.Add(green < red)

# The green house is next to the white one (adjacent)
# |green - white| == 1
diff_gw = model.NewIntVar(-4, 4, 'diff_gw')
model.Add(diff_gw == green - white)
abs_gw = model.NewIntVar(0, 4, 'abs_gw')
model.AddAbsEquality(abs_gw, diff_gw)
model.Add(abs_gw == 1)

# The Norwegian lives on the right of the blue house
model.Add(norway == blue + 1)

# The doctor drinks milk
model.Add(doctor == milk)

# The diplomat is Japanese
model.Add(diplomat == japan)

# The Norwegian owns the zebra
model.Add(norway == zebra)

# The horse is owned by the neighbor of the diplomat
# |horse - diplomat| == 1
diff_hd = model.NewIntVar(-4, 4, 'diff_hd')
model.Add(diff_hd == horse - diplomat)
abs_hd = model.NewIntVar(0, 4, 'abs_hd')
model.AddAbsEquality(abs_hd, diff_hd)
model.Add(abs_hd == 1)

# The Italian either lives in the red, white or green house
# italy == red or italy == white or italy == green
b_red = model.NewBoolVar('italy_red')
b_white = model.NewBoolVar('italy_white')
b_green = model.NewBoolVar('italy_green')

model.Add(italy == red).OnlyEnforceIf(b_red)
model.Add(italy != red).OnlyEnforceIf(b_red.Not())

model.Add(italy == white).OnlyEnforceIf(b_white)
model.Add(italy != white).OnlyEnforceIf(b_white.Not())

model.Add(italy == green).OnlyEnforceIf(b_green)
model.Add(italy != green).OnlyEnforceIf(b_green.Not())

model.AddBoolOr([b_red, b_white, b_green])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'colors': {
            'yellow': solver.Value(yellow),
            'green': solver.Value(green),
            'red': solver.Value(red),
            'white': solver.Value(white),
            'blue': solver.Value(blue)
        },
        'nations': {
            'italy': solver.Value(italy),
            'spain': solver.Value(spain),
            'japan': solver.Value(japan),
            'england': solver.Value(england),
            'norway': solver.Value(norway)
        },
        'pets': {
            'cat': solver.Value(cat),
            'zebra': solver.Value(zebra),
            'bear': solver.Value(bear),
            'snails': solver.Value(snails),
            'horse': solver.Value(horse)
        },
        'drinks': {
            'milk': solver.Value(milk),
            'water': solver.Value(water),
            'tea': solver.Value(tea),
            'coffee': solver.Value(coffee),
            'juice': solver.Value(juice)
        },
        'jobs': {
            'painter': solver.Value(painter),
            'sculptor': solver.Value(sculptor),
            'diplomat': solver.Value(diplomat),
            'pianist': solver.Value(pianist),
            'doctor': solver.Value(doctor)
        }
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
