# Jobs puzzle: four people (indices 0-3) hold eight different jobs, and each person
# holds exactly two jobs. Output: for each job, the index of the person who holds it.
import mip

JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
PEOPLE = range(4)


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[j][p] = 1 when person p holds job j
    x = {
        j: {p: model.add_var(f"x_{j}_{p}", var_type=mip.BINARY) for p in PEOPLE}
        for j in JOBS
    }
    # holder[j] = index of the person who holds job j
    holder = {
        j: model.add_var(f"holder_{j}", lb=0, ub=3, var_type=mip.INTEGER) for j in JOBS
    }

    # Four people hold eight different jobs: each job is held by exactly one person.
    for j in JOBS:
        model.add_constr(mip.xsum(x[j][p] for p in PEOPLE) == 1)
        model.add_constr(holder[j] == mip.xsum(p * x[j][p] for p in PEOPLE))

    # Each person holds exactly two jobs.
    for p in PEOPLE:
        model.add_constr(mip.xsum(x[j][p] for j in JOBS) == 2)

    def not_same_person(a, b):
        for p in PEOPLE:
            model.add_constr(x[a][p] + x[b][p] <= 1)

    # Clue 1: The nurse is not a teacher, police officer, or clerk.
    not_same_person("nurse", "teacher")
    not_same_person("nurse", "police_officer")
    not_same_person("nurse", "clerk")

    # Clue 2: The clerk is not the chef.
    not_same_person("clerk", "chef")

    # Clue 3: Person 0 is not the boxer.
    model.add_constr(x["boxer"][0] == 0)

    # Clue 4: Person 3 is not the teacher, police officer, or nurse.
    model.add_constr(x["teacher"][3] == 0)
    model.add_constr(x["police_officer"][3] == 0)
    model.add_constr(x["nurse"][3] == 0)

    # Clue 5: Person 0, the chef, and the police officer went golfing together.
    # Three people, so person 0, the chef and the police officer are pairwise distinct.
    model.add_constr(x["chef"][0] == 0)
    model.add_constr(x["police_officer"][0] == 0)
    not_same_person("chef", "police_officer")

    outputs = {j: holder[j] for j in JOBS}
    return model, outputs
