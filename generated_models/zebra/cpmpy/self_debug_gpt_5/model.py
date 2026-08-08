
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# Each array maps the item (by index in the specified order) to a house index 0..4 (left to right)
colors  = cp.intvar(0,4, shape=5, name="colors")   # [yellow, green, red, white, blue]
nations = cp.intvar(0,4, shape=5, name="nations")  # [italy, spain, japan, england, norway]
pets    = cp.intvar(0,4, shape=5, name="pets")     # [cat, zebra, bear, snails, horse]
drinks  = cp.intvar(0,4, shape=5, name="drinks")   # [milk, water, tea, coffee, juice]
jobs    = cp.intvar(0,4, shape=5, name="jobs")     # [painter, sculptor, diplomat, pianist, doctor]

# Constraints
# All entries in each category are assigned to different houses
model += cp.AllDifferent(colors)
model += cp.AllDifferent(nations)
model += cp.AllDifferent(pets)
model += cp.AllDifferent(drinks)
model += cp.AllDifferent(jobs)

# Helper indices (for readability)
YELLOW, GREEN, RED, WHITE, BLUE = 0, 1, 2, 3, 4
ITALY, SPAIN, JAPAN, ENGLAND, NORWAY = 0, 1, 2, 3, 4
CAT, ZEBRA, BEAR, SNAILS, HORSE = 0, 1, 2, 3, 4
MILK, WATER, TEA, COFFEE, JUICE = 0, 1, 2, 3, 4
PAINTER, SCULPTOR, DIPLOMAT, PIANIST, DOCTOR = 0, 1, 2, 3, 4

# Given clues as constraints:
# - the painter owns the horse
model += (jobs[PAINTER] == pets[HORSE])
# - the diplomat drinks coffee
model += (jobs[DIPLOMAT] == drinks[COFFEE])
# - the one who drinks milk lives in the white house
model += (drinks[MILK] == colors[WHITE])
# - the Spaniard is a painter
model += (nations[SPAIN] == jobs[PAINTER])
# - the Englishman lives in the red house
model += (nations[ENGLAND] == colors[RED])
# - the snails are owned by the sculptor
model += (pets[SNAILS] == jobs[SCULPTOR])
# - the green house is immediately on the left of the red one
model += (colors[GREEN] + 1 == colors[RED])
# - the Norwegian lives immediately on the right of the blue house
model += (nations[NORWAY] == colors[BLUE] + 1)
# - the doctor drinks milk
model += (jobs[DOCTOR] == drinks[MILK])
# - the diplomat is Japanese
model += (jobs[DIPLOMAT] == nations[JAPAN])
# - the Norwegian owns the zebra
model += (nations[NORWAY] == pets[ZEBRA])
# - the green house is next to the white one
model += (cp.Abs(colors[GREEN] - colors[WHITE]) == 1)
# - the horse is owned by the neighbor of the diplomat
model += (cp.Abs(pets[HORSE] - jobs[DIPLOMAT]) == 1)
# - the Italian either lives in the red, white or green house
model += ((nations[ITALY] == colors[RED]) | (nations[ITALY] == colors[WHITE]) | (nations[ITALY] == colors[GREEN]))

# Solve and print
if model.solve():
    solution = {
        'colors': colors.value().tolist(),
        'nations': nations.value().tolist(),
        'jobs': jobs.value().tolist(),
        'pets': pets.value().tolist(),
        'drinks': drinks.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
