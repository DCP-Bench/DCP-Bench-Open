from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Constants for indexing
Debra, Janet, Hugh, Rick = 0, 1, 2, 3
people = [Debra, Janet, Hugh, Rick]

# Allergies and surnames indices
eggs, mold, nuts, ragweed = 0, 1, 2, 3
baxter, lemon, malone, fleet = 0, 1, 2, 3

# Decision variables
# allergy[i] = allergy index for person i
allergy = [model.NewIntVar(0, 3, f'allergy_{i}') for i in people]
# surname[i] = surname index for person i
surname = [model.NewIntVar(0, 3, f'surname_{i}') for i in people]

# All allergies are different
model.AddAllDifferent(allergy)
# All surnames are different
model.AddAllDifferent(surname)

# Constraints from the problem

# Rick is not allergic to mold
model.Add(allergy[Rick] != mold)

# Baxter is allergic to eggs
# Find person with surname Baxter, that person's allergy is eggs
for i in people:
    # Create boolean variable: is_baxter[i] = (surname[i] == baxter)
    is_baxter = model.NewBoolVar(f'is_baxter_{i}')
    model.Add(surname[i] == baxter).OnlyEnforceIf(is_baxter)
    model.Add(surname[i] != baxter).OnlyEnforceIf(is_baxter.Not())
    # If is_baxter then allergy[i] == eggs
    model.Add(allergy[i] == eggs).OnlyEnforceIf(is_baxter)

# Hugh is neither surnamed Lemon nor Fleet
model.Add(surname[Hugh] != lemon)
model.Add(surname[Hugh] != fleet)

# Debra is allergic to ragweed
model.Add(allergy[Debra] == ragweed)

# Janet (who isn't Lemon) is neither allergic to eggs nor to mold
model.Add(surname[Janet] != lemon)
model.Add(allergy[Janet] != eggs)
model.Add(allergy[Janet] != mold)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'eggs': [solver.Value(allergy[i]) for i in people],
        'mold': [solver.Value(allergy[i]) for i in people],
        'nuts': [solver.Value(allergy[i]) for i in people],
        'ragweed': [solver.Value(allergy[i]) for i in people],
        'baxter': [solver.Value(surname[i]) for i in people],
        'lemon': [solver.Value(surname[i]) for i in people],
        'malone': [solver.Value(surname[i]) for i in people],
        'fleet': [solver.Value(surname[i]) for i in people]
    }
    # The problem asks to print the values of each food and surname for each friend.
    # The keys should be the food and surname names as given, and the values should be lists of length 4,
    # where the i-th element corresponds to the person i (Debra=0, Janet=1, Hugh=2, Rick=3).
    # But the current solution repeats the allergy and surname lists for each food and surname key.
    # Instead, we should print the allergy and surname assignments per person, but the problem wants the values of each food and surname for each friend.
    # So we need to create for each food and surname a list of 4 booleans indicating if that person has that allergy or surname.

    # Create dictionary with keys as food and surname names, values as lists of 0/1 indicating if person i has that allergy/surname
    allergy_names = ['eggs', 'mold', 'nuts', 'ragweed']
    surname_names = ['baxter', 'lemon', 'malone', 'fleet']

    allergy_solution = {}
    for a in allergy_names:
        a_idx = allergy_names.index(a)
        allergy_solution[a] = [1 if solver.Value(allergy[i]) == a_idx else 0 for i in people]

    surname_solution = {}
    for s in surname_names:
        s_idx = surname_names.index(s)
        surname_solution[s] = [1 if solver.Value(surname[i]) == s_idx else 0 for i in people]

    # Merge dictionaries
    solution = {**allergy_solution, **surname_solution}

    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")