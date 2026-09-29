# Jobs puzzle: four people hold eight different jobs, two each, subject to
# clues about who is not what.
from hermax.model import Model

JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n_people = 4

    m = Model()
    # job[name] = the person, 0-3, who holds that job
    job = {name: m.int(name, 0, n_people - 1) for name in JOBS}

    # every person holds exactly two jobs
    for person in range(n_people):
        m &= (sum(1 * (job[name] == person) for name in JOBS) == 2)

    # 1. the nurse is not the teacher, the police officer or the clerk
    m &= (job["nurse"] != job["teacher"])
    m &= (job["nurse"] != job["police_officer"])
    m &= (job["nurse"] != job["clerk"])
    # 2. the clerk is not the chef
    m &= (job["clerk"] != job["chef"])
    # 3. person 0 is not the boxer
    m &= (job["boxer"] != 0)
    # 4. person 3 is not the teacher, the police officer or the nurse
    m &= (job["teacher"] != 3)
    m &= (job["police_officer"] != 3)
    m &= (job["nurse"] != 3)
    # 5. person 0, the chef and the police officer went golfing together, so they
    # are three different people
    m &= (job["chef"] != 0)
    m &= (job["police_officer"] != 0)
    m &= (job["chef"] != job["police_officer"])

    return m, job
