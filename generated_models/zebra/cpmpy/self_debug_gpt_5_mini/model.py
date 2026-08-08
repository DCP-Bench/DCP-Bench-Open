
import cpmpy as cp
import json

# Data / ordering (index in each list corresponds to the item)
# colors:  yellow, green, red, white, blue
# nations: italy, spain, japan, england, norway
# pets:    cat, zebra, bear, snails, horse
# drinks:  milk, water, tea, coffee, juice
# jobs:    painter, sculptor, diplomat, pianist, doctor

# Model definition
model = cp.Model()

# Decision Variables: house indices 0..4 for each item in the given order
colors = cp.intvar(0, 4, shape=5, name="colors")
nations = cp.intvar(0, 4, shape=5, name="nations")
pets = cp.intvar(0, 4, shape=5, name="pets")
drinks = cp.intvar(0, 4, shape=5, name="drinks")
jobs = cp.intvar(0, 4, shape=5, name="jobs")

# Each category is a permutation of the houses (all different)
model += cp.AllDifferent(colors)
model += cp.AllDifferent(nations)
model += cp.AllDifferent(pets)
model += cp.AllDifferent(drinks)
model += cp.AllDifferent(jobs)

# Constraints from the puzzle (using the indices from the orderings above)

# the painter owns the horse
model += jobs[0] == pets[4]

# the diplomat drinks coffee
model += jobs[2] == drinks[3]

# the one who drinks milk lives in the white house
model += drinks[0] == colors[3]

# the Spaniard is a painter
model += nations[1] == jobs[0]

# the Englishman lives in the red house
model += nations[3] == colors[2]

# the snails are owned by the sculptor
model += pets[3] == jobs[1]

# the green house is immediately on the left of the red one
model += colors[1] + 1 == colors[2]

# the Norwegian lives immediately on the right of the blue house
model += nations[4] == colors[4] + 1

# the doctor drinks milk
model += jobs[4] == drinks[0]

# the diplomat is Japanese
model += nations[2] == jobs[2]

# the Norwegian owns the zebra
model += nations[4] == pets[1]

# the green house is next to the white one
model += cp.Abs(colors[1] - colors[3]) == 1

# the horse is owned by the neighbor of the diplomat
model += cp.Abs(pets[4] - jobs[2]) == 1

# the Italian either lives in the red, white or green house
model += (nations[0] == colors[2]) | (nations[0] == colors[3]) | (nations[0] == colors[1])

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
