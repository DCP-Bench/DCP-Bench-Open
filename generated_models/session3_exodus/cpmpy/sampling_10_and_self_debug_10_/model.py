
import cpmpy as cp
import json

# Data ordering (indexes):
# Ages:    index 0->3, 1->5, 2->7, 3->8, 4->10
# Children: index 0->Bernice,1->Carl,2->Debby,3->Sammy,4->Ted
# Countries: index 0->Ethiopia,1->Kazakhstan,2->Lithuania,3->Morocco,4->Yemen
# Stories: index 0->burning bush,1->captivity,2->Moses's youth,3->Passover,4->Ten Commandments

model = cp.Model()

# Person ids will be 0..4 (we will convert to 1..5 in the output)
# ages[a] = person id (0..4) who has age corresponding to ages index a
ages = cp.intvar(0, 4, shape=5, name="ages")        # ages[0]=person with age 3, ages[1]=person with age 5, ...
children = cp.intvar(0, 4, shape=5, name="children")# children[0]=person id of Bernice, etc.
countries = cp.intvar(0, 4, shape=5, name="countries")
stories = cp.intvar(0, 4, shape=5, name="stories")

# Each list is a permutation of persons 0..4
model += cp.AllDifferent(ages)
model += cp.AllDifferent(children)
model += cp.AllDifferent(countries)
model += cp.AllDifferent(stories)

# Inverse mapping: for each person p (0..4), person_age_index[p] is the age-index (0..4)
person_age_index = cp.intvar(0, 4, shape=5, name="person_age_index")
model += cp.Inverse(ages, person_age_index)

# Numeric age values corresponding to age indexes
ages_values = [3, 5, 7, 8, 10]

# person_age[p] is the numeric age (3,5,7,8,10) of person p
person_age = cp.intvar(3, 10, shape=5, name="person_age")
for p in range(5):
    model += person_age[p] == cp.Element(ages_values, person_age_index[p])

# Constraints as given in the puzzle (using 0-based indexes):
# 1. Debby’s family is from Lithuania.
#    Debby is children[2]; Lithuania is countries[2]
model += children[2] == countries[2]

# 2. The child who told the story of the Passover is two years older than Bernice.
#    Passover is stories[3]; Bernice is children[0]
model += cp.Element(person_age, stories[3]) == cp.Element(person_age, children[0]) + 2

# 3. The child whose family is from Yemen is younger than the child from the Ethiopian family.
#    Yemen is countries[4]; Ethiopia is countries[0]
model += cp.Element(person_age, countries[4]) < cp.Element(person_age, countries[0])

# 4. The child from the Moroccan family is three years older than Ted.
#    Morocco is countries[3]; Ted is children[4]
model += cp.Element(person_age, countries[3]) == cp.Element(person_age, children[4]) + 3

# 5. Sammy is three years older than the child who told the story of Moses’s youth.
#    Sammy is children[3]; Moses's youth is stories[2]
model += cp.Element(person_age, children[3]) == cp.Element(person_age, stories[2]) + 3

# Solve
if model.solve():
    # Convert 0-based person ids to 1-based as requested (values 1..5)
    ages_out = [int(x + 1) for x in ages.value().tolist()]
    children_out = [int(x + 1) for x in children.value().tolist()]
    countries_out = [int(x + 1) for x in countries.value().tolist()]
    stories_out = [int(x + 1) for x in stories.value().tolist()]

    solution = {
        'ages': ages_out,
        'children': children_out,
        'countries': countries_out,
        'stories': stories_out
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
