
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables (1..5 represent group IDs)
ages = cp.intvar(1, 5, shape=5, name="ages")         # [three, five, seven, eight, ten]
children = cp.intvar(1, 5, shape=5, name="children") # [Bernice, Carl, Debby, Sammy, Ted]
countries = cp.intvar(1, 5, shape=5, name="countries") # [Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen]
stories = cp.intvar(1, 5, shape=5, name="stories")   # [burning bush, captivity, Moses's youth, Passover, Ten Commandments]

# All are permutations of 1..5
model += cp.AllDifferent(ages)
model += cp.AllDifferent(children)
model += cp.AllDifferent(countries)
model += cp.AllDifferent(stories)

# Helper: Inverse mapping for ages to use numeric age differences
# ages maps age_index -> group; inv_ages maps group_index(0..4) -> age_index
ages0 = cp.intvar(0, 4, shape=5, name="ages0")
inv_ages = cp.intvar(0, 4, shape=5, name="inv_ages")
model += (ages0 == ages - 1)
model += cp.Inverse(ages0, inv_ages)

# Numeric ages corresponding to indices [three, five, seven, eight, ten]
age_nums = [3, 5, 7, 8, 10]

# Convenience lambdas for numeric age of a group (group IDs are 1..5)
num_age_of_group = lambda g: cp.Element(age_nums, inv_ages[g - 1])

# Indices for readability
# children: 0 Bernice, 1 Carl, 2 Debby, 3 Sammy, 4 Ted
# countries: 0 Ethiopia, 1 Kazakhstan, 2 Lithuania, 3 Morocco, 4 Yemen
# stories: 0 burning bush, 1 captivity, 2 Moses's youth, 3 Passover, 4 Ten Commandments

# Constraints from clues:
# 1. Debby’s family is from Lithuania.
model += (children[2] == countries[2])

# 2. Passover is two years older than Bernice.
model += (num_age_of_group(stories[3]) == num_age_of_group(children[0]) + 2)

# 3. Yemen child is younger than Ethiopian child.
model += (num_age_of_group(countries[4]) < num_age_of_group(countries[0]))

# 4. Moroccan family child is three years older than Ted.
model += (num_age_of_group(countries[3]) == num_age_of_group(children[4]) + 3)

# 5. Sammy is three years older than the child who told Moses’s youth.
model += (num_age_of_group(children[3]) == num_age_of_group(stories[2]) + 3)

# Solve and print
if model.solve():
    solution = {
        'ages': ages.value().tolist(),
        'children': children.value().tolist(),
        'countries': countries.value().tolist(),
        'stories': stories.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
