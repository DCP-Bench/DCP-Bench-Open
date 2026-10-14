"""Jobs puzzle: four people hold eight jobs, two each; find who holds which job from five clues."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: four people, eight jobs, as stated.
PEOPLE = range(4)
JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
JOBS_PER_PERSON = 2


def build(instance):
    model = gp.Model("jobs_puzzle")

    # holds[job, p] = 1 when person p holds that job; each job has one holder.
    holds = model.addVars(JOBS, PEOPLE, vtype=GRB.BINARY, name="holds")
    for job in JOBS:
        model.addConstr(holds.sum(job, "*") == 1, name=f"one_holder[{job}]")

    # Each person holds exactly two jobs.
    for p in PEOPLE:
        model.addConstr(holds.sum("*", p) == JOBS_PER_PERSON, name=f"two_jobs[{p}]")

    def different_people(job1, job2):
        for p in PEOPLE:
            model.addConstr(holds[job1, p] + holds[job2, p] <= 1, name=f"{job1}_not_{job2}[{p}]")

    def not_person(job, p):
        model.addConstr(holds[job, p] == 0, name=f"{job}_not_person[{p}]")

    # 1. The nurse is not the teacher, the police officer, or the clerk.
    for job in ("teacher", "police_officer", "clerk"):
        different_people("nurse", job)

    # 2. The clerk is not the chef.
    different_people("clerk", "chef")

    # 3. Person 0 is not the boxer.
    not_person("boxer", 0)

    # 4. Person 3 is not the teacher, the police officer, or the nurse.
    for job in ("teacher", "police_officer", "nurse"):
        not_person(job, 3)

    # 5. Person 0, the chef and the police officer went golfing together, so
    #    they are three different people.
    not_person("chef", 0)
    not_person("police_officer", 0)
    different_people("chef", "police_officer")

    # The person index holding each job.
    return model, {job: gp.quicksum(p * holds[job, p] for p in PEOPLE) for job in JOBS}
