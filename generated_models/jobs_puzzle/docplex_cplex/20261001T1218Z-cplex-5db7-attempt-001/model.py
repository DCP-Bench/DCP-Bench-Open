"""Jobs puzzle: four people hold eight different jobs, two each. From five clues, find who
holds which job.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data: four people (0..3), eight jobs, two jobs each.
    num_people = 4
    jobs_per_person = 2
    names = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
    people = range(num_people)

    model = Model("jobs_puzzle")

    # holds[j, p] is 1 when person p holds job j; every job has one holder.
    holds = {(j, p): model.binary_var(name=f"{j}_held_by_{p}") for j in names for p in people}
    for j in names:
        model.add_constraint(model.sum(holds[j, p] for p in people) == 1)

    # Each person holds exactly two jobs.
    for p in people:
        model.add_constraint(model.sum(holds[j, p] for j in names) == jobs_per_person)

    def different(j1, j2):
        # Jobs j1 and j2 have different holders: no person holds both.
        for p in people:
            model.add_constraint(holds[j1, p] + holds[j2, p] <= 1)

    def not_held_by(j, p):
        model.add_constraint(holds[j, p] == 0)

    # 1. The nurse is not the teacher, the police officer or the clerk.
    different("nurse", "teacher")
    different("nurse", "police_officer")
    different("nurse", "clerk")
    # 2. The clerk is not the chef.
    different("clerk", "chef")
    # 3. Person 0 is not the boxer.
    not_held_by("boxer", 0)
    # 4. Person 3 is not the teacher, the police officer or the nurse.
    not_held_by("teacher", 3)
    not_held_by("police_officer", 3)
    not_held_by("nurse", 3)
    # 5. Person 0, the chef and the police officer went golfing together: three different
    # people.
    not_held_by("chef", 0)
    not_held_by("police_officer", 0)
    different("chef", "police_officer")

    # The holder of each job.
    holder = {j: model.integer_var(0, num_people - 1, name=j) for j in names}
    for j in names:
        model.add_constraint(holder[j] == model.sum(p * holds[j, p] for p in people))

    return model, dict(holder)
