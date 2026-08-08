
import cpmpy as cp
import json

# Constants for indices (for readability)
yellow, green, red, white, blue = 0, 1, 2, 3, 4
italy, spain, japan, england, norway = 0, 1, 2, 3, 4
cat, zebra, bear, snails, horse = 0, 1, 2, 3, 4
milk, water, tea, coffee, juice = 0, 1, 2, 3, 4
painter, sculptor, diplomat, pianist, doctor = 0, 1, 2, 3, 4

model = cp.Model()

houses = range(1, 6)  # Houses numbered 1 to 5 from left to right

# Decision variables: the house number of each attribute
colors = cp.intvar(1, 5, shape=5, name="colors")
nations = cp.intvar(1, 5, shape=5, name="nations")
pets = cp.intvar(1, 5, shape=5, name="pets")
drinks = cp.intvar(1, 5, shape=5, name="drinks")
jobs = cp.intvar(1, 5, shape=5, name="jobs")

# All attributes in each category are distinct houses
model += cp.AllDifferent(colors)
model += cp.AllDifferent(nations)
model += cp.AllDifferent(pets)
model += cp.AllDifferent(drinks)
model += cp.AllDifferent(jobs)

# The painter owns the horse
model += jobs[painter] == pets[horse]

# The diplomat drinks coffee
model += jobs[diplomat] == drinks[coffee]

# The one who drinks milk lives in the white house
model += drinks[milk] == colors[white]

# The Spaniard is a painter
model += nations[spain] == jobs[painter]

# The Englishman lives in the red house
model += nations[england] == colors[red]

# The snails are owned by the sculptor
model += pets[snails] == jobs[sculptor]

# The green house is on the left of the red one (somewhere to the left)
model += colors[green] < colors[red]

# The Norwegian lives on the right of the blue house (somewhere to the right)
model += nations[norway] > colors[blue]

# The doctor drinks milk
model += jobs[doctor] == drinks[milk]

# The diplomat is Japanese
model += jobs[diplomat] == nations[japan]

# The Norwegian owns the zebra
model += nations[norway] == pets[zebra]

# The green house is next to the white one (neighboring houses)
model += cp.abs(colors[green] - colors[white]) == 1

# The horse is owned by the neighbor of the diplomat (neighbor means difference of 1)
model += cp.abs(pets[horse] - jobs[diplomat]) == 1

# The Italian either lives in the red, white or green house
model += (nations[italy] == colors[red]) | (nations[italy] == colors[white]) | (nations[italy] == colors[green])

# Solve and print
if model.solve():
    solution = {
        "colors": colors.value().tolist(),
        "nations": nations.value().tolist(),
        "jobs": jobs.value().tolist(),
        "pets": pets.value().tolist(),
        "drinks": drinks.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
