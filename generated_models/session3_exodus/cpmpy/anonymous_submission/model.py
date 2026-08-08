from cpmpy import *
import json

# Decision Variables
# Categories: ages (3,5,7,8,10), children (Bernice=0, Carl=1, Debby=2, Sammy=3, Ted=4),
# countries (Ethiopia=0, Kazakhstan=1, Lithuania=2, Morocco=3, Yemen=4),
# stories (burning bush=0, captivity=1, Moses's youth=2, Passover=3, Ten Commandments=4)

# Use actual age values with proper bounds
ages = intvar(3, 10, shape=5, name="ages")  # ages[child] = actual age (3-10)
countries = intvar(0, 4, shape=5, name="countries")  # countries[child] = country index
stories = intvar(0, 4, shape=5, name="stories")  # stories[child] = story index

# Model
model = Model()

# All variables must be distinct within each category
model += AllDifferent(ages)
model += AllDifferent(countries)
model += AllDifferent(stories)

# Constraint 1: Debby's family is from Lithuania (Debby=2, Lithuania=2)
model += countries[2] == 2

# Constraint 2: The child who told the story of the Passover is two years older than Bernice
passover_child = intvar(0,4, name="passover_child")
for i in range(5):
    model += (stories[i] == 3).implies(passover_child == i)
model += ages[passover_child] == ages[0] + 2  # Comparing actual ages

# Constraint 3: The child from Yemen is younger than the child from Ethiopia
yemen_child = intvar(0,4, name="yemen_child")
ethiopia_child = intvar(0,4, name="ethiopia_child")
for i in range(5):
    model += (countries[i] == 4).implies(yemen_child == i)
    model += (countries[i] == 0).implies(ethiopia_child == i)
model += ages[yemen_child] < ages[ethiopia_child]

# Constraint 4: The child from Morocco is three years older than Ted
morocco_child = intvar(0,4, name="morocco_child")
for i in range(5):
    model += (countries[i] == 3).implies(morocco_child == i)
model += ages[morocco_child] == ages[4] + 3  # Comparing actual ages

# Constraint 5: Sammy is three years older than the child who told the story of Moses's youth
moses_child = intvar(0,4, name="moses_child")
for i in range(5):
    model += (stories[i] == 2).implies(moses_child == i)
model += ages[3] == ages[moses_child] + 3  # Comparing actual ages

# Solve
model.solve()

# Prepare solution
solution = {
    "ages": ages.value().tolist(),
    "children": [0,1,2,3,4],  # Fixed order: Bernice, Carl, Debby, Sammy, Ted
    "countries": countries.value().tolist(),
    "stories": stories.value().tolist()
}

print(json.dumps(solution))