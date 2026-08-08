from cpmpy import *
import json

# Parameters
n = 5  # Number of children, ages, countries, and stories

# Decision variables
children = intvar(1, n, shape=n, name="children")  # 1: Bernice, 2: Carl, 3: Debby, 4: Sammy, 5: Ted
countries = intvar(1, n, shape=n, name="countries")  # 1: Ethiopia, 2: Kazakhstan, 3: Lithuania, 4: Morocco, 5: Yemen
stories = intvar(1, n, shape=n, name="stories")  # 1: burning bush, 2: captivity, 3: Moses’s youth, 4: Passover, 5: Ten Commandments
ages = intvar([3, 5, 7, 8, 10], shape=n, name="ages")  # Ages: 3, 5, 7, 8, 10

# Model
model = Model()

# All variables must be unique (one-to-one mapping)
model += [AllDifferent(children)]
model += [AllDifferent(countries)]
model += [AllDifferent(stories)]
model += [AllDifferent(ages)]

# 1. Debby’s family is from Lithuania.
model += [children[2] == 3]  # Debby is the third child
model += [countries[2] == 3]  # Lithuania is the third country

# 2. The child who told the story of the Passover is two years older than Bernice.
# Use element-wise indexing to find the index of the Passover story and Bernice
passover_index = intvar(0, n-1, name="passover_index")
bernice_index = intvar(0, n-1, name="bernice_index")
model += [stories[passover_index] == 4]
model += [children[bernice_index] == 1]
model += [ages[passover_index] == ages[bernice_index] + 2]

# 3. The child whose family is from Yemen is younger than the child from the Ethiopian family.
yemen_index = intvar(0, n-1, name="yemen_index")
ethiopia_index = intvar(0, n-1, name="ethiopia_index")
model += [countries[yemen_index] == 5]
model += [countries[ethiopia_index] == 1]
model += [ages[yemen_index] < ages[ethiopia_index]]

# 4. The child from the Moroccan family is three years older than Ted.
morocco_index = intvar(0, n-1, name="morocco_index")
ted_index = intvar(0, n-1, name="ted_index")
model += [countries[morocco_index] == 4]
model += [children[ted_index] == 5]
model += [ages[morocco_index] == ages[ted_index] + 3]

# 5. Sammy is three years older than the child who told the story of Moses’s youth in the house of the Pharaoh.
sammy_index = intvar(0, n-1, name="sammy_index")
moses_index = intvar(0, n-1, name="moses_index")
model += [children[sammy_index] == 4]
model += [stories[moses_index] == 3]
model += [ages[sammy_index] == ages[moses_index] + 3]

# Solve the model
model.solve()

# Print the solution
solution = {
    "children": children.value().tolist(),
    "countries": countries.value().tolist(),
    "stories": stories.value().tolist(),
    "ages": ages.value().tolist()
}
print(json.dumps(solution))