from paramita.modelling import Bool

# Four people hold eight different jobs, each person holds exactly two jobs.
# Each job is held by one person; h[job][p] is true when person p holds the job (one-hot over people).

JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
PEOPLE = range(4)


def build(instance):
    h = {j: {p: Bool(f"holds_{j}_{p}") for p in PEOPLE} for j in JOBS}
    cons = []

    # each job is held by exactly one person
    for j in JOBS:
        cons.append(sum(h[j].values()) == 1)

    # each person holds exactly two jobs
    for p in PEOPLE:
        cons.append(sum(h[j][p] for j in JOBS) == 2)

    # clue 1: the nurse is not a teacher, police officer, or clerk
    # (no person holds the nurse job together with one of these)
    for other in ["teacher", "police_officer", "clerk"]:
        for p in PEOPLE:
            cons.append(~(h["nurse"][p] & h[other][p]))

    # clue 2: the clerk is not the chef
    for p in PEOPLE:
        cons.append(~(h["clerk"][p] & h["chef"][p]))

    # clue 3: person 0 is not the boxer
    cons.append(~h["boxer"][0])

    # clue 4: person 3 is not the teacher, police officer, or nurse
    for j in ["teacher", "police_officer", "nurse"]:
        cons.append(~h[j][3])

    # clue 5: person 0, the chef, and the police officer went golfing together
    # (three different people: person 0 is neither the chef nor the police officer,
    # and the chef and the police officer are different people)
    cons.append(~h["chef"][0])
    cons.append(~h["police_officer"][0])
    for p in PEOPLE:
        cons.append(~(h["chef"][p] & h["police_officer"][p]))

    # output: for each job, the index of the person who holds it
    outputs = {j: sum(p * h[j][p] for p in PEOPLE) for j in JOBS}
    return cons, outputs
