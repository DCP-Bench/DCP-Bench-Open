"""Jobs puzzle: four people hold eight different jobs, two each. From the clues, determine
which person holds which jobs.

The model reports, for each job, the person (0..3) who holds it.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    people = range(4)
    jobs = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]

    problem = pulp.LpProblem("jobs_puzzle", pulp.LpMinimize)  # satisfaction

    # holds[job][p] = 1 if person p holds the job; every job has one holder
    holds = {job: [pulp.LpVariable(f"holds_{job}_{p}", cat="Binary") for p in people]
             for job in jobs}
    for job in jobs:
        problem += pulp.lpSum(holds[job]) == 1

    # each person holds exactly two jobs
    for p in people:
        problem += pulp.lpSum(holds[job][p] for job in jobs) == 2

    def different(job1, job2):
        """the two jobs are held by different people"""
        for p in people:
            problem.addConstraint(holds[job1][p] + holds[job2][p] <= 1)

    # 1. The nurse is not a teacher, police officer, or clerk.
    for other in ("teacher", "police_officer", "clerk"):
        different("nurse", other)
    # 2. The clerk is not the chef.
    different("clerk", "chef")
    # 3. Person 0 is not the boxer.
    problem += holds["boxer"][0] == 0
    # 4. Person 3 is not the teacher, police officer, or nurse.
    for job in ("teacher", "police_officer", "nurse"):
        problem += holds[job][3] == 0
    # 5. Person 0, the chef, and the police officer went golfing together: three people
    problem += holds["chef"][0] == 0
    problem += holds["police_officer"][0] == 0
    different("chef", "police_officer")

    return problem, {job: pulp.lpSum(p * var for p, var in zip(people, holds[job])) for job in jobs}
