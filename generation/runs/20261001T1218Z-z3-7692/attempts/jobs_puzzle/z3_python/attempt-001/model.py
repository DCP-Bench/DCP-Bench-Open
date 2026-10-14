# Jobs puzzle: four people hold eight different jobs, two each. From five clues,
# work out which person holds which jobs.
import z3


def build(instance):
    del instance  # the puzzle states its own people and jobs

    num_people = 4
    num_jobs = 8

    # jobs[j] = the person (0-3) who holds job j.
    chef, guard, nurse, clerk, police_officer, teacher, actor, boxer = jobs = z3.IntVector("jobs", num_jobs)

    solver = z3.Solver()
    for person in jobs:
        solver.add(person >= 0, person <= num_people - 1)

    # Each person holds exactly two jobs.
    for p in range(num_people):
        solver.add(z3.PbEq([(job == p, 1) for job in jobs], 2))

    # 1. The nurse is not a teacher, police officer, or clerk.
    solver.add(nurse != teacher, nurse != police_officer, nurse != clerk)

    # 2. The clerk is not the chef.
    solver.add(clerk != chef)

    # 3. Person 0 is not the boxer.
    solver.add(boxer != 0)

    # 4. Person 3 is not the teacher, police officer, or nurse.
    solver.add(teacher != 3, police_officer != 3, nurse != 3)

    # 5. Person 0, the chef and the police officer went golfing together, so they
    #    are three different people.
    solver.add(chef != 0, police_officer != 0, chef != police_officer)

    return solver, {
        "chef": chef, "guard": guard, "nurse": nurse, "clerk": clerk,
        "police_officer": police_officer, "teacher": teacher, "actor": actor,
        "boxer": boxer,
    }
