# Jobs puzzle: four people hold eight jobs, two each. From five clues, find who holds which job.
from pychoco.model import Model

# The puzzle has no instance data; the people, jobs and clues are its statement.
NUM_PEOPLE = 4
JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
JOBS_EACH = 2


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # job[name] = the person (0..3) holding that job
    job = {name: model.intvar(0, NUM_PEOPLE - 1, name=name) for name in JOBS}

    # Each person holds exactly two jobs.
    people = list(range(NUM_PEOPLE))
    held = [model.intvar(JOBS_EACH, JOBS_EACH, name=f"held_{p}") for p in people]
    model.global_cardinality([job[name] for name in JOBS], people, held).post()

    # 1. The nurse is not the teacher, the police officer or the clerk.
    for other in ("teacher", "police_officer", "clerk"):
        model.arithm(job["nurse"], "!=", job[other]).post()
    # 2. The clerk is not the chef.
    model.arithm(job["clerk"], "!=", job["chef"]).post()
    # 3. Person 0 is not the boxer.
    model.arithm(job["boxer"], "!=", 0).post()
    # 4. Person 3 is not the teacher, the police officer or the nurse.
    for name in ("teacher", "police_officer", "nurse"):
        model.arithm(job[name], "!=", 3).post()
    # 5. Person 0, the chef and the police officer went golfing together: three different people.
    model.arithm(job["chef"], "!=", 0).post()
    model.arithm(job["police_officer"], "!=", 0).post()
    model.arithm(job["chef"], "!=", job["police_officer"]).post()

    return model, job
