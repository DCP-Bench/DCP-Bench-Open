# Jobs puzzle: four people hold eight different jobs (chef, guard, nurse, clerk,
# police officer, teacher, actor, boxer). Each person holds exactly two jobs.
# For each job the output is the index (0-3) of the person who holds it.
import cvc5.pythonic as cz

JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
PEOPLE = range(4)


def build(instance):
    h = {job: cz.Int(job) for job in JOBS}
    constraints = []

    # Each job is held by one of the four people, indexed 0-3.
    for job in JOBS:
        constraints += [h[job] >= 0, h[job] <= 3]

    # Four people hold eight different jobs. Each person holds exactly two jobs.
    for p in PEOPLE:
        constraints.append(cz.Sum([cz.If(h[job] == p, 1, 0) for job in JOBS]) == 2)

    # Clue 1: The nurse is not a teacher, police officer, or clerk.
    for job in ["teacher", "police_officer", "clerk"]:
        constraints.append(h["nurse"] != h[job])

    # Clue 2: The clerk is not the chef.
    constraints.append(h["clerk"] != h["chef"])

    # Clue 3: Person 0 is not the boxer.
    constraints.append(h["boxer"] != 0)

    # Clue 4: Person 3 is not the teacher, police officer, or nurse.
    for job in ["teacher", "police_officer", "nurse"]:
        constraints.append(h[job] != 3)

    # Clue 5: Person 0, the chef, and the police officer went golfing together.
    # Three different people: person 0, the chef, and the police officer.
    constraints += [
        h["chef"] != 0,
        h["police_officer"] != 0,
        h["chef"] != h["police_officer"],
    ]

    outputs = {job: h[job] for job in JOBS}
    return constraints, outputs
