from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# We have 4 shoes and 4 stores, each bought/visited in order 1 to 4
# Variables represent the order in which each shoe/store was bought/visited
ecruespadrilles = model.NewIntVar(1, 4, 'ecruespadrilles')
fuchsiaflats = model.NewIntVar(1, 4, 'fuchsiaflats')
purplepumps = model.NewIntVar(1, 4, 'purplepumps')
suedesandals = model.NewIntVar(1, 4, 'suedesandals')

footfarm = model.NewIntVar(1, 4, 'footfarm')
heelsinahandcart = model.NewIntVar(1, 4, 'heelsinahandcart')
theshoepalace = model.NewIntVar(1, 4, 'theshoepalace')
tootsies = model.NewIntVar(1, 4, 'tootsies')

# All shoes bought at different times
model.AddAllDifferent([ecruespadrilles, fuchsiaflats, purplepumps, suedesandals])
# All stores visited at different times
model.AddAllDifferent([footfarm, heelsinahandcart, theshoepalace, tootsies])

# 1. Harriet bought fuchsia flats at Heels in a Handcart.
model.Add(fuchsiaflats == heelsinahandcart)

# 2. The store she visited just after buying her purple pumps was not Tootsies.
# So the order of purplepumps + 1 = store visited next, and that store != tootsies
# We need to link the shoe order to the store order for the next stop.
# So find the store visited at purplepumps + 1, it is not tootsies.
# We can express this by saying that the store visited at time purplepumps + 1 != tootsies
# We can create a variable for the store visited at purplepumps + 1 and constrain it.

# Create an array of stores indexed by time 1..4
stores = [footfarm, heelsinahandcart, theshoepalace, tootsies]

# We create a variable for the store visited just after purplepumps
next_store_after_pumps = model.NewIntVar(1, 4, 'next_store_after_pumps')

# Constraint: next_store_after_pumps == store visited at time purplepumps + 1
# We use AddElement: next_store_after_pumps == stores[purplepumps]
# But purplepumps is 1-based, AddElement is 0-based index, so index = purplepumps - 1 + 1 = purplepumps
# So index = purplepumps (1-based) means index in 0..3 is purplepumps - 1
# The next store is at time purplepumps + 1, so index = purplepumps (1-based)
# So index for AddElement is purplepumps (1-based) - 1 = purplepumps - 1, but we want purplepumps + 1 - 1 = purplepumps
# So index = purplepumps (1-based)
# So we want next_store_after_pumps == stores[purplepumps] where purplepumps is 1-based index for the store visited after purplepumps

# So index for AddElement is purplepumps (1-based) for the next store after purplepumps
# But purplepumps is a variable, so index = purplepumps (1-based)
# We want to get store at time purplepumps + 1, so index = purplepumps + 1 - 1 = purplepumps
# So index = purplepumps (1-based) for the next store after purplepumps

# So we create an intermediate variable for purplepumps + 1
purplepumps_plus_1 = model.NewIntVar(2, 5, 'purplepumps_plus_1')
model.Add(purplepumps_plus_1 == purplepumps + 1)

# But purplepumps_plus_1 can be 5, which is invalid time, so we add a constraint that purplepumps < 4
model.Add(purplepumps < 4)

# Now next_store_after_pumps = stores[purplepumps_plus_1 - 1]
model.AddElement(purplepumps_plus_1 - 1, stores, next_store_after_pumps)

# The store visited just after purple pumps is not tootsies
model.Add(next_store_after_pumps != tootsies)

# 3. The Foot Farm was Harriet's second stop.
model.Add(footfarm == 2)

# 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
# So suedesandals == theshoepalace + 2
model.Add(suedesandals == theshoepalace + 2)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'ecruespadrilles': solver.Value(ecruespadrilles),
        'fuchsiaflats': solver.Value(fuchsiaflats),
        'purplepumps': solver.Value(purplepumps),
        'suedesandals': solver.Value(suedesandals),
        'footfarm': solver.Value(footfarm),
        'heelsinahandcart': solver.Value(heelsinahandcart),
        'theshoepalace': solver.Value(theshoepalace),
        'tootsies': solver.Value(tootsies)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")