
import cpmpy as cp
import json

# Constants for indexing
colors = ["yellow", "green", "red", "white", "blue"]
nations = ["italy", "spain", "japan", "england", "norway"]
pets = ["cat", "zebra", "bear", "snails", "horse"]
drinks = ["milk", "water", "tea", "coffee", "juice"]
jobs = ["painter", "sculptor", "diplomat", "pianist", "doctor"]

# Number of houses
n = 5

# Model definition
model = cp.Model()

# Decision variables: house number for each attribute value (1 to 5)
color_vars = cp.intvar(1, n, shape=len(colors), name="color")
nation_vars = cp.intvar(1, n, shape=len(nations), name="nation")
pet_vars = cp.intvar(1, n, shape=len(pets), name="pet")
drink_vars = cp.intvar(1, n, shape=len(drinks), name="drink")
job_vars = cp.intvar(1, n, shape=len(jobs), name="job")

# All different constraints for each category
model += cp.AllDifferent(color_vars)
model += cp.AllDifferent(nation_vars)
model += cp.AllDifferent(pet_vars)
model += cp.AllDifferent(drink_vars)
model += cp.AllDifferent(job_vars)

# Helper function to get index of an attribute
def idx(lst, val):
    return lst.index(val)

# Constraints from the puzzle

# The painter owns the horse
model += job_vars[idx(jobs, "painter")] == pet_vars[idx(pets, "horse")]

# The diplomat drinks coffee
model += job_vars[idx(jobs, "diplomat")] == drink_vars[idx(drinks, "coffee")]

# The one who drinks milk lives in the white house
model += drink_vars[idx(drinks, "milk")] == color_vars[idx(colors, "white")]

# The Spaniard is a painter
model += nation_vars[idx(nations, "spain")] == job_vars[idx(jobs, "painter")]

# The Englishman lives in the red house
model += nation_vars[idx(nations, "england")] == color_vars[idx(colors, "red")]

# The snails are owned by the sculptor
model += pet_vars[idx(pets, "snails")] == job_vars[idx(jobs, "sculptor")]

# The green house is on the left of the red one
model += color_vars[idx(colors, "green")] + 1 == color_vars[idx(colors, "red")]

# The Norwegian lives on the right of the blue house
model += nation_vars[idx(nations, "norway")] == color_vars[idx(colors, "blue")] + 1

# The doctor drinks milk
model += job_vars[idx(jobs, "doctor")] == drink_vars[idx(drinks, "milk")]

# The diplomat is Japanese
model += job_vars[idx(jobs, "diplomat")] == nation_vars[idx(nations, "japan")]

# The Norwegian owns the zebra
model += nation_vars[idx(nations, "norway")] == pet_vars[idx(pets, "zebra")]

# The green house is next to the white one
model += cp.Abs(color_vars[idx(colors, "green")] - color_vars[idx(colors, "white")]) == 1

# The horse is owned by the neighbor of the diplomat
model += cp.Abs(pet_vars[idx(pets, "horse")] - job_vars[idx(jobs, "diplomat")]) == 1

# The Italian either lives in the red, white or green house
italian_house = nation_vars[idx(nations, "italy")]
model += (italian_house == color_vars[idx(colors, "red")]) | \
         (italian_house == color_vars[idx(colors, "white")]) | \
         (italian_house == color_vars[idx(colors, "green")])

# Solve and print
if model.solve():
    solution = {
        'colors': color_vars.value().tolist(),
        'nations': nation_vars.value().tolist(),
        'jobs': job_vars.value().tolist(),
        'pets': pet_vars.value().tolist(),
        'drinks': drink_vars.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
