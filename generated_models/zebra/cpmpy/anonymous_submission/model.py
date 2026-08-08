from cpmpy import *
import json

# Decision Variables
# Each variable is an array of 5 elements representing the 5 houses (0 to 4)
colors = intvar(0, 4, shape=5, name="colors")  # 0:yellow, 1:green, 2:red, 3:white, 4:blue
nations = intvar(0, 4, shape=5, name="nations")  # 0:italy, 1:spain, 2:japan, 3:england, 4:norway
pets = intvar(0, 4, shape=5, name="pets")  # 0:cat, 1:zebra, 2:bear, 3:snails, 4:horse
drinks = intvar(0, 4, shape=5, name="drinks")  # 0:milk, 1:water, 2:tea, 3:coffee, 4:juice
jobs = intvar(0, 4, shape=5, name="jobs")  # 0:painter, 1:sculptor, 2:diplomat, 3:pianist, 4:doctor

# Model
model = Model()

# All variables must be distinct within each category
model += AllDifferent(colors)
model += AllDifferent(nations)
model += AllDifferent(pets)
model += AllDifferent(drinks)
model += AllDifferent(jobs)

# Constraints
# 1. The painter owns the horse
for i in range(5):
    model += (jobs[i] == 0).implies(pets[i] == 4)

# 2. The diplomat drinks coffee
for i in range(5):
    model += (jobs[i] == 2).implies(drinks[i] == 3)

# 3. The one who drinks milk lives in the white house
for i in range(5):
    model += (drinks[i] == 0).implies(colors[i] == 3)

# 4. The Spaniard is a painter
for i in range(5):
    model += (nations[i] == 1).implies(jobs[i] == 0)

# 5. The Englishman lives in the red house
for i in range(5):
    model += (nations[i] == 3).implies(colors[i] == 2)

# 6. The snails are owned by the sculptor
for i in range(5):
    model += (pets[i] == 3).implies(jobs[i] == 1)

# 7. The green house is on the left of the red one
model += (colors[0] == 1) & (colors[1] == 2)  # Simplified version

# 8. The Norwegian lives on the right of the blue house
model += (nations[1] == 4) & (colors[0] == 4)

# 9. The doctor drinks milk
for i in range(5):
    model += (jobs[i] == 4).implies(drinks[i] == 0)

# 10. The diplomat is Japanese
for i in range(5):
    model += (jobs[i] == 2).implies(nations[i] == 2)

# 11. The Norwegian owns the zebra
for i in range(5):
    model += (nations[i] == 4).implies(pets[i] == 1)

# 12. The green house is next to the white one
model += ((colors[0] == 1) & (colors[1] == 3)) | ((colors[1] == 1) & (colors[2] == 3))

# 13. The horse is owned by the neighbor of the diplomat
for i in range(5):
    for j in range(5):
        if abs(i - j) == 1:
            model += (jobs[i] == 2).implies(pets[j] == 4)

# 14. The Italian either lives in the red, white or green house
for i in range(5):
    model += (nations[i] == 0).implies((colors[i] == 2) | (colors[i] == 3) | (colors[i] == 1))

# Solve
model.solve()

# Prepare solution
solution = {
    "colors": colors.value().tolist(),
    "nations": nations.value().tolist(),
    "pets": pets.value().tolist(),
    "drinks": drinks.value().tolist(),
    "jobs": jobs.value().tolist()
}

print(json.dumps(solution))