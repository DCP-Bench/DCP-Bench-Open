from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# We have 5 children: Bernice, Carl, Debby, Sammy, Ted
# 5 ages: 3, 5, 7, 8, 10
# 5 countries: Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen
# 5 stories: burning bush, captivity, Moses’s youth, Passover, Ten Commandments

# We will represent each category as a list of 5 variables, each variable's value is from 1 to 5
# The index corresponds to the entity in the order:
# children: [Bernice, Carl, Debby, Sammy, Ted]
# ages: 3,5,7,8,10 mapped to 1..5 (1=3, 2=5, 3=7, 4=8, 5=10)
# countries: [Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen]
# stories: [burning bush, captivity, Moses’s youth, Passover, Ten Commandments]

# The value at position i in each list corresponds to the mapping index (1..5) that links the entities.
# For example, ages[i] = k means the ith child has the kth age in the age list.

# Create variables for each category: each is a permutation of 1..5
children = ['Bernice', 'Carl', 'Debby', 'Sammy', 'Ted']
ages = [model.NewIntVar(1, 5, f'age_{c}') for c in children]
countries = [model.NewIntVar(1, 5, f'country_{c}') for c in children]
stories = [model.NewIntVar(1, 5, f'story_{c}') for c in children]

# All ages, countries, stories are permutations (all different)
model.AddAllDifferent(ages)
model.AddAllDifferent(countries)
model.AddAllDifferent(stories)

# Helper dictionaries for mapping names to indices
child_idx = {name: i for i, name in enumerate(children)}
country_idx = {'Ethiopia': 1, 'Kazakhstan': 2, 'Lithuania': 3, 'Morocco': 4, 'Yemen': 5}
story_idx = {'burning bush': 1, 'captivity': 2, "Moses’s youth": 3, 'Passover': 4, 'Ten Commandments': 5}
age_val = {1: 3, 2: 5, 3: 7, 4: 8, 5: 10}  # mapping from 1..5 to actual ages

# 1. Debby’s family is from Lithuania.
model.Add(countries[child_idx['Debby']] == country_idx['Lithuania'])

# 2. The child who told the story of the Passover is two years older than Bernice.
# Find the age index of Bernice and Passover storyteller, then their actual ages differ by 2
# ages are mapped 1..5 to 3,5,7,8,10
# So we need to enforce: age_val[ages[passover_child]] - age_val[ages[Bernice]] == 2
# We don't know who told Passover, so we find the child with story == Passover (4)
# We create an intermediate variable for the index of the Passover child
passover_child = model.NewIntVar(0, 4, 'passover_child')
# Link passover_child to the child whose story is Passover (4)
for i in range(5):
    model.Add(passover_child == i).OnlyEnforceIf(stories[i] == story_idx['Passover'])
    model.Add(passover_child != i).OnlyEnforceIf(stories[i] != story_idx['Passover'])

# We need to express age difference: age_val[ages[passover_child]] - age_val[ages[Bernice]] == 2
# Since age_val is not linear, we create auxiliary variables for ages of Bernice and Passover child
bern_age = ages[child_idx['Bernice']]
passover_age = model.NewIntVar(1, 5, 'passover_age')

# Link passover_age to ages[passover_child]
# We create 5 boolean variables for passover_child == i
passover_is = [model.NewBoolVar(f'passover_is_{i}') for i in range(5)]
model.Add(passover_child == 0).OnlyEnforceIf(passover_is[0])
model.Add(passover_child != 0).OnlyEnforceIf(passover_is[0].Not())
model.Add(passover_child == 1).OnlyEnforceIf(passover_is[1])
model.Add(passover_child != 1).OnlyEnforceIf(passover_is[1].Not())
model.Add(passover_child == 2).OnlyEnforceIf(passover_is[2])
model.Add(passover_child != 2).OnlyEnforceIf(passover_is[2].Not())
model.Add(passover_child == 3).OnlyEnforceIf(passover_is[3])
model.Add(passover_child != 3).OnlyEnforceIf(passover_is[3].Not())
model.Add(passover_child == 4).OnlyEnforceIf(passover_is[4])
model.Add(passover_child != 4).OnlyEnforceIf(passover_is[4].Not())

# passover_age = sum(ages[i] * passover_is[i])
model.Add(passover_age == sum(ages[i] * passover_is[i] for i in range(5)))

# Now enforce age_val[passover_age] - age_val[bern_age] == 2
# We can do this by enumerating all possible pairs (a,b) with age_val[a] - age_val[b] == 2
# Create allowed pairs for (bern_age, passover_age)
allowed_pairs = []
for b in range(1, 6):
    for p in range(1, 6):
        if age_val[p] - age_val[b] == 2:
            allowed_pairs.append((b, p))
model.AddAllowedAssignments([bern_age, passover_age], allowed_pairs)

# 3. The child whose family is from Yemen is younger than the child from the Ethiopian family.
# So age of Yemen child < age of Ethiopia child
# Find indices of Yemen and Ethiopia children
yemen_child = model.NewIntVar(0, 4, 'yemen_child')
ethiopia_child = model.NewIntVar(0, 4, 'ethiopia_child')

for i in range(5):
    model.Add(yemen_child == i).OnlyEnforceIf(countries[i] == country_idx['Yemen'])
    model.Add(yemen_child != i).OnlyEnforceIf(countries[i] != country_idx['Yemen'])
    model.Add(ethiopia_child == i).OnlyEnforceIf(countries[i] == country_idx['Ethiopia'])
    model.Add(ethiopia_child != i).OnlyEnforceIf(countries[i] != country_idx['Ethiopia'])

# Get ages of Yemen and Ethiopia children
yemen_age = model.NewIntVar(1, 5, 'yemen_age')
ethiopia_age = model.NewIntVar(1, 5, 'ethiopia_age')

yemen_is = [model.NewBoolVar(f'yemen_is_{i}') for i in range(5)]
ethiopia_is = [model.NewBoolVar(f'ethiopia_is_{i}') for i in range(5)]

for i in range(5):
    model.Add(yemen_child == i).OnlyEnforceIf(yemen_is[i])
    model.Add(yemen_child != i).OnlyEnforceIf(yemen_is[i].Not())
    model.Add(ethiopia_child == i).OnlyEnforceIf(ethiopia_is[i])
    model.Add(ethiopia_child != i).OnlyEnforceIf(ethiopia_is[i].Not())

model.Add(yemen_age == sum(ages[i] * yemen_is[i] for i in range(5)))
model.Add(ethiopia_age == sum(ages[i] * ethiopia_is[i] for i in range(5)))

# Enforce yemen_age < ethiopia_age
model.Add(yemen_age < ethiopia_age)

# 4. The child from the Moroccan family is three years older than Ted.
# Find Moroccan child index and Ted index (Ted is fixed index)
ted_idx = child_idx['Ted']
morocco_child = model.NewIntVar(0, 4, 'morocco_child')
for i in range(5):
    model.Add(morocco_child == i).OnlyEnforceIf(countries[i] == country_idx['Morocco'])
    model.Add(morocco_child != i).OnlyEnforceIf(countries[i] != country_idx['Morocco'])

# Get ages of Moroccan child and Ted
morocco_age = model.NewIntVar(1, 5, 'morocco_age')
ted_age = ages[ted_idx]

morocco_is = [model.NewBoolVar(f'morocco_is_{i}') for i in range(5)]
for i in range(5):
    model.Add(morocco_child == i).OnlyEnforceIf(morocco_is[i])
    model.Add(morocco_child != i).OnlyEnforceIf(morocco_is[i].Not())
model.Add(morocco_age == sum(ages[i] * morocco_is[i] for i in range(5)))

# Enforce age_val[morocco_age] - age_val[ted_age] == 3
allowed_pairs_4 = []
for t in range(1, 6):
    for m in range(1, 6):
        if age_val[m] - age_val[t] == 3:
            allowed_pairs_4.append((t, m))
model.AddAllowedAssignments([ted_age, morocco_age], allowed_pairs_4)

# 5. Sammy is three years older than the child who told the story of Moses’s youth in the house of the Pharaoh.
# Sammy index
sammy_idx = child_idx['Sammy']
sammy_age = ages[sammy_idx]

# Find Moses’s youth storyteller index
moses_child = model.NewIntVar(0, 4, 'moses_child')
for i in range(5):
    model.Add(moses_child == i).OnlyEnforceIf(stories[i] == story_idx["Moses’s youth"])
    model.Add(moses_child != i).OnlyEnforceIf(stories[i] != story_idx["Moses’s youth"])

moses_is = [model.NewBoolVar(f'moses_is_{i}') for i in range(5)]
for i in range(5):
    model.Add(moses_child == i).OnlyEnforceIf(moses_is[i])
    model.Add(moses_child != i).OnlyEnforceIf(moses_is[i].Not())

moses_age = model.NewIntVar(1, 5, 'moses_age')
model.Add(moses_age == sum(ages[i] * moses_is[i] for i in range(5)))

# Enforce age_val[sammy_age] - age_val[moses_age] == 3
allowed_pairs_5 = []
for m in range(1, 6):
    for s in range(1, 6):
        if age_val[s] - age_val[m] == 3:
            allowed_pairs_5.append((m, s))
model.AddAllowedAssignments([moses_age, sammy_age], allowed_pairs_5)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # We need to print ages, children, countries, stories as lists of integers from 1 to 5,
    # where the same number represents a mapping between the four categories.
    # The lists should be in the order of children: Bernice, Carl, Debby, Sammy, Ted
    # Each list element is the mapping index (1..5) that links the categories.

    # ages[i] is the age index for child i
    # countries[i] is the country index for child i
    # stories[i] is the story index for child i

    ages_sol = [solver.Value(ages[i]) for i in range(5)]
    children_sol = [i+1 for i in range(5)]  # children are fixed order, so 1..5
    countries_sol = [solver.Value(countries[i]) for i in range(5)]
    stories_sol = [solver.Value(stories[i]) for i in range(5)]

    solution = {
        'ages': ages_sol,
        'children': children_sol,
        'countries': countries_sol,
        'stories': stories_sol
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")