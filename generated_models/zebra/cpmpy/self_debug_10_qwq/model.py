
import cpmpy as cp
import json

# Define variables for each category's house numbers (1-5)
color_house = cp.intvar(1, 5, shape=5, name="color_house")  # 0:yellow, 1:green, 2:red, 3:white, 4:blue
nation_house = cp.intvar(1, 5, shape=5, name="nation_house")  # 0:italy, 1:spain, 2:japan, 3:england, 4:norway
job_house = cp.intvar(1, 5, shape=5, name="job_house")       # 0:painter, 1:sculptor, 2:diplomat, 3:pianist, 4:doctor
pet_house = cp.intvar(1, 5, shape=5, name="pet_house")       # 0:cat, 1:zebra, 2:bear, 3:snails, 4:horse
drink_house = cp.intvar(1, 5, shape=5, name="drink_house")   # 0:milk, 1:water, 2:tea, 3:coffee, 4:juice

model = cp.Model()

# All variables in each category must be distinct (permutation of 1-5)
model += [cp.AllDifferent(color_house),
          cp.AllDifferent(nation_house),
          cp.AllDifferent(job_house),
          cp.AllDifferent(pet_house),
          cp.AllDifferent(drink_house)]

# Constraints based on the problem's clues
model += (job_house[0] == pet_house[4])  # Painter owns horse
model += (job_house[2] == drink_house[3])  # Diplomat drinks coffee
model += (drink_house[0] == color_house[3])  # Milk in white house
model += (nation_house[1] == job_house[0])  # Spaniard is painter
model += (nation_house[3] == color_house[2])  # Englishman in red house
model += (pet_house[3] == job_house[1])  # Sculptor owns snails
model += (color_house[1] < color_house[2])  # Green left of red
model += (nation_house[4] > color_house[4])  # Norwegian right of blue
model += (job_house[4] == drink_house[0])  # Doctor drinks milk
model += (job_house[2] == nation_house[2])  # Diplomat is Japanese
model += (nation_house[4] == pet_house[1])  # Norwegian owns zebra
model += (cp.Abs(color_house[1] - color_house[3]) == 1)  # Green adjacent to white
model += (cp.Abs(job_house[2] - pet_house[4]) == 1)  # Horse neighbor of diplomat
model += (cp.any([nation_house[0] == color_house[2],  # Italian in red, white, or green
                 nation_house[0] == color_house[3],
                 nation_house[0] == color_house[1]]))

# Solve and output
if model.solve():
    solution = {
        'colors': color_house.value().tolist(),
        'nations': nation_house.value().tolist(),
        'jobs': job_house.value().tolist(),
        'pets': pet_house.value().tolist(),
        'drinks': drink_house.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
