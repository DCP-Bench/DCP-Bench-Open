# Jobs puzzle: four people hold eight different jobs, two each, subject to
# clues about who is not what.
from exact import Exact

JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n_people = 4

    solver = Exact()
    # holds[name][p] = 1 when person p holds the job; job[name] is that person
    holds = {name: [f"{name}_held_by_{p}" for p in range(n_people)] for name in JOBS}
    for name in JOBS:
        solver.addVariable(name, 0, n_people - 1)
        for var in holds[name]:
            solver.addVariable(var, 0, 1)
        # every job is held by exactly one person
        solver.addConstraint([(1, var) for var in holds[name]], True, 1, True, 1)
        solver.addConstraint([(p, holds[name][p]) for p in range(1, n_people)] + [(-1, name)],
                             True, 0, True, 0)

    # every person holds exactly two jobs
    for p in range(n_people):
        solver.addConstraint([(1, holds[name][p]) for name in JOBS], True, 2, True, 2)

    def apart(first, second):
        # the two jobs are held by different people
        for p in range(n_people):
            solver.addConstraint([(1, holds[first][p]), (1, holds[second][p])], False, 0, True, 1)

    def not_held_by(name, person):
        solver.addConstraint([(1, holds[name][person])], False, 0, True, 0)

    # 1. the nurse is not the teacher, the police officer or the clerk
    apart("nurse", "teacher")
    apart("nurse", "police_officer")
    apart("nurse", "clerk")
    # 2. the clerk is not the chef
    apart("clerk", "chef")
    # 3. person 0 is not the boxer
    not_held_by("boxer", 0)
    # 4. person 3 is not the teacher, the police officer or the nurse
    not_held_by("teacher", 3)
    not_held_by("police_officer", 3)
    not_held_by("nurse", 3)
    # 5. person 0, the chef and the police officer went golfing together, so they
    # are three different people
    not_held_by("chef", 0)
    not_held_by("police_officer", 0)
    apart("chef", "police_officer")

    return solver, {name: name for name in JOBS}
