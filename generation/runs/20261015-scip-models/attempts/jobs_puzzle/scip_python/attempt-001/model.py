# Jobs puzzle: four people hold eight different jobs, each person holds exactly two.
# Output: the person index (0-3) holding each job.

from pyscipopt import Model, quicksum

JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
PEOPLE = range(4)


def build(instance):
    m = Model()

    # x[p, job] = 1 if person p holds the job
    x = {(p, job): m.addVar(name=f"x_{p}_{job}", vtype="B") for p in PEOPLE for job in JOBS}

    # each job is held by exactly one person
    for job in JOBS:
        # every job has exactly one holder
        m.addCons(quicksum(x[p, job] for p in PEOPLE) == 1)

    # each person holds exactly two jobs
    for p in PEOPLE:
        # each person holds exactly two jobs
        m.addCons(quicksum(x[p, job] for job in JOBS) == 2)

    # clue 1: the nurse is not a teacher, police officer, or clerk
    for p in PEOPLE:
        # the nurse is not a teacher
        m.addCons(x[p, "nurse"] + x[p, "teacher"] <= 1)
        # the nurse is not a police officer
        m.addCons(x[p, "nurse"] + x[p, "police_officer"] <= 1)
        # the nurse is not a clerk
        m.addCons(x[p, "nurse"] + x[p, "clerk"] <= 1)

    # clue 2: the clerk is not the chef
    for p in PEOPLE:
        # the clerk is not the chef
        m.addCons(x[p, "clerk"] + x[p, "chef"] <= 1)

    # clue 3: person 0 is not the boxer
    m.addCons(x[0, "boxer"] == 0)

    # clue 4: person 3 is not the teacher, police officer, or nurse
    m.addCons(x[3, "teacher"] + x[3, "police_officer"] + x[3, "nurse"] == 0)

    # clue 5: person 0, the chef, and the police officer went golfing together,
    # read as three different people: the chef and the police officer are
    # distinct from each other and from person 0
    m.addCons(x[0, "chef"] + x[0, "police_officer"] == 0)
    for p in PEOPLE:
        # the chef and the police officer are not the same person
        m.addCons(x[p, "chef"] + x[p, "police_officer"] <= 1)

    # the output gives the person index holding each job
    outputs = {job: quicksum(p * x[p, job] for p in PEOPLE) for job in JOBS}
    return m, {
        "chef": outputs["chef"],
        "guard": outputs["guard"],
        "nurse": outputs["nurse"],
        "clerk": outputs["clerk"],
        "police_officer": outputs["police_officer"],
        "teacher": outputs["teacher"],
        "actor": outputs["actor"],
        "boxer": outputs["boxer"],
    }
