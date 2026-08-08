from cpmpy import *
import json

# Parameters
n_houses = 5  # Number of houses

# Define categories and their possible values
colors_names = ["yellow", "green", "red", "white", "blue"]
jobs_names = ["painter", "sculptor", "diplomat", "pianist", "doctor"]
nations_names = ["italy", "spain", "japan", "england", "norway"]
pets_names = ["cat", "zebra", "bear", "snails", "horse"]
drinks_names = ["milk", "water", "tea", "coffee", "juice"]

# Map names to indices for easier reference
colors_index = {name: i for i, name in enumerate(colors_names)}
jobs_index = {name: i for i, name in enumerate(jobs_names)}
nations_index = {name: i for i, name in enumerate(nations_names)}
pets_index = {name: i for i, name in enumerate(pets_names)}
drinks_index = {name: i for i, name in enumerate(drinks_names)}

# Decision variables: for each category, assign a house (0 to 4) to each value
colors = intvar(0, n_houses - 1, shape=len(colors_names), name="colors")
jobs = intvar(0, n_houses - 1, shape=len(jobs_names), name="jobs")
nations = intvar(0, n_houses - 1, shape=len(nations_names), name="nations")
pets = intvar(0, n_houses - 1, shape=len(pets_names), name="pets")
drinks = intvar(0, n_houses - 1, shape=len(drinks_names), name="drinks")

# Model
model = Model()

# All variables must be permutations (each value appears exactly once)
model += [AllDifferent(colors)]
model += [AllDifferent(jobs)]
model += [AllDifferent(nations)]
model += [AllDifferent(pets)]
model += [AllDifferent(drinks)]

# The painter owns the horse
model += [jobs[jobs_index["painter"]] == pets[pets_index["horse"]]]

# The diplomat drinks coffee
model += [jobs[jobs_index["diplomat"]] == drinks[drinks_index["coffee"]]]

# The one who drinks milk lives in the white house
model += [drinks[drinks_index["milk"]] == colors[colors_index["white"]]]

# The Spaniard is a painter
model += [nations[nations_index["spain"]] == jobs[jobs_index["painter"]]]

# The Englishman lives in the red house
model += [nations[nations_index["england"]] == colors[colors_index["red"]]]

# The snails are owned by the sculptor
model += [pets[pets_index["snails"]] == jobs[jobs_index["sculptor"]]]

# The green house is on the left of the red one
model += [colors[colors_index["green"]] == colors[colors_index["red"]] - 1]

# The Norwegian lives on the right of the blue house
model += [nations[nations_index["norway"]] == colors[colors_index["blue"]] + 1]

# The doctor drinks milk
model += [jobs[jobs_index["doctor"]] == drinks[drinks_index["milk"]]]

# The diplomat is Japanese
model += [jobs[jobs_index["diplomat"]] == nations[nations_index["japan"]]]

# The Norwegian owns the zebra
model += [nations[nations_index["norway"]] == pets[pets_index["zebra"]]]

# The green house is next to the white one
model += [abs(colors[colors_index["green"]] - colors[colors_index["white"]]) == 1]

# The horse is owned by the neighbor of the diplomat
model += [abs(pets[pets_index["horse"]] - jobs[jobs_index["diplomat"]]) == 1]

# The Italian either lives in the red, white or green house
model += [(nations[nations_index["italy"]] == colors[colors_index["red"]]) |
          (nations[nations_index["italy"]] == colors[colors_index["white"]]) |
          (nations[nations_index["italy"]] == colors[colors_index["green"]])]

# Solve the model
model.solve()

# Print the solution
solution = {
    "colors": colors.value().tolist(),
    "jobs": jobs.value().tolist(),
    "nations": nations.value().tolist(),
    "pets": pets.value().tolist(),
    "drinks": drinks.value().tolist()
}
print(json.dumps(solution))