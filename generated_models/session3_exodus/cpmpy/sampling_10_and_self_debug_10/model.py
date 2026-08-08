
import cpmpy as cp
import json

# Data
children_names = ["Bernice", "Carl", "Debby", "Sammy", "Ted"]
ages_values = [3, 5, 7, 8, 10]
countries_names = ["Ethiopia", "Kazakhstan", "Lithuania", "Morocco", "Yemen"]
stories_names = ["burning bush", "captivity", "Moses’s youth", "Passover", "Ten Commandments"]

model = cp.Model()

# Decision variables
ages = cp.intvar(0,4,shape=5,name="ages")       # ages[i] = age index of child i
countries = cp.intvar(0,4,shape=5,name="countries") # countries[i] = country index of child i
stories = cp.intvar(0,4,shape=5,name="stories")     # stories[i] = story index of child i

# All different constraints
model += cp.AllDifferent(ages)
model += cp.AllDifferent(countries)
model += cp.AllDifferent(stories)

def child_idx(name):
    return children_names.index(name)

# Constraint 1
model += (countries[child_idx("Debby")] == 2)

# Constraint 2
bernice_age_val = cp.intvar(3,10,name="bernice_age_val")
passover_age_val = cp.intvar(3,10,name="passover_age_val")
model += (bernice_age_val == cp.Element(ages_values, ages[child_idx("Bernice")]))
passover_child_idx = cp.intvar(0,4,name="passover_child_idx")
model += cp.Count(stories, 3) == 1
for i in range(5):
    model += (stories[i] == 3).implies(passover_child_idx == i)
model += (stories[passover_child_idx] == 3)
model += (passover_age_val == cp.Element(ages_values, ages[passover_child_idx]))
model += (passover_age_val == bernice_age_val + 2)

# Constraint 3
yemen_child_idx = cp.intvar(0,4,name="yemen_child_idx")
ethiopia_child_idx = cp.intvar(0,4,name="ethiopia_child_idx")
model += cp.Count(countries, 4) == 1
model += cp.Count(countries, 0) == 1
for i in range(5):
    model += (countries[i] == 4).implies(yemen_child_idx == i)
    model += (countries[i] == 0).implies(ethiopia_child_idx == i)
yemen_age_val = cp.intvar(3,10,name="yemen_age_val")
ethiopia_age_val = cp.intvar(3,10,name="ethiopia_age_val")
model += (yemen_age_val == cp.Element(ages_values, ages[yemen_child_idx]))
model += (ethiopia_age_val == cp.Element(ages_values, ages[ethiopia_child_idx]))
model += (yemen_age_val < ethiopia_age_val)

# Constraint 4
morocco_child_idx = cp.intvar(0,4,name="morocco_child_idx")
model += cp.Count(countries, 3) == 1
for i in range(5):
    model += (countries[i] == 3).implies(morocco_child_idx == i)
ted_age_val = cp.intvar(3,10,name="ted_age_val")
morocco_age_val = cp.intvar(3,10,name="morocco_age_val")
model += (ted_age_val == cp.Element(ages_values, ages[child_idx("Ted")]))
model += (morocco_age_val == cp.Element(ages_values, ages[morocco_child_idx]))
model += (morocco_age_val == ted_age_val + 3)

# Constraint 5
sammy_age_val = cp.intvar(3,10,name="sammy_age_val")
moses_youth_child_idx = cp.intvar(0,4,name="moses_youth_child_idx")
model += cp.Count(stories, 2) == 1
for i in range(5):
    model += (stories[i] == 2).implies(moses_youth_child_idx == i)
model += (sammy_age_val == cp.Element(ages_values, ages[child_idx("Sammy")]))
moses_youth_age_val = cp.intvar(3,10,name="moses_youth_age_val")
model += (moses_youth_age_val == cp.Element(ages_values, ages[moses_youth_child_idx]))
model += (sammy_age_val == moses_youth_age_val + 3)

if model.solve():
    # ages: for each age index, find child i with ages[i] == age_index, assign i+1
    ages_list = [0]*5
    for age_index in range(5):
        for i in range(5):
            if ages[i].value() == age_index:
                ages_list[age_index] = i+1
                break

    # children: for each child i, assign i+1
    children_list = [i+1 for i in range(5)]

    # countries: for each country index, find child i with countries[i] == country_index, assign i+1
    countries_list = [0]*5
    for country_index in range(5):
        for i in range(5):
            if countries[i].value() == country_index:
                countries_list[country_index] = i+1
                break

    # stories: for each story index, find child i with stories[i] == story_index, assign i+1
    stories_list = [0]*5
    for story_index in range(5):
        for i in range(5):
            if stories[i].value() == story_index:
                stories_list[story_index] = i+1
                break

    solution = {
        'ages': ages_list,
        'children': children_list,
        'countries': countries_list,
        'stories': stories_list
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
