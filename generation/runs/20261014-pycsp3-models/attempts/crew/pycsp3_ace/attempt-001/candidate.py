from pycsp3 import *

# assign the flight attendants to the flights, with the crew sizes and required languages per flight
n_flights = len(data.required_crew)
n_people = len(data.attributes)
n_langs = len(data.required_crew[0]) - 3
# crew[f][p] is 1 if person p is assigned to flight f
crew = VarArray(size=[n_flights, n_people], dom={0, 1})
satisfy(
    # each flight needs its number of cabin crew
    [Sum(crew[f]) == data.required_crew[f][0] for f in range(n_flights)],
    # each flight needs enough stewards
    [Sum(crew[f][p] * data.attributes[p][0] for p in range(n_people)) >= data.required_crew[f][1] for f in range(n_flights)],
    # each flight needs enough hostesses
    [Sum(crew[f][p] * data.attributes[p][1] for p in range(n_people)) >= data.required_crew[f][2] for f in range(n_flights)],
    # each flight needs enough speakers of each required language
    [Sum(crew[f][p] * data.attributes[p][2 + k] for p in range(n_people)) >= data.required_crew[f][3 + k]
     for f in range(n_flights) for k in range(n_langs)],
    # every cabin crew member has two flights off after an attended flight
    [crew[f][p] + crew[g][p] <= 1
     for p in range(n_people) for f in range(n_flights) for g in range(f + 1, min(f + 3, n_flights))],
)
