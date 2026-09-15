import cpmpy as cp


def build(instance):
    """Jobs puzzle: four people hold eight jobs, two each.

    The puzzle states its own people, jobs and clues, so `instance` is unused.
    Each variable holds the index of the person doing that job.
    """
    del instance

    num_people = 4
    num_jobs = 8

    jobs = cp.intvar(0, num_people - 1, shape=num_jobs, name="jobs")
    chef, guard, nurse, clerk, police_officer, teacher, actor, boxer = jobs

    model = cp.Model()
    # Each person holds exactly two jobs.
    for i in range(num_people):
        model += cp.sum([jobs[j] == i for j in range(num_jobs)]) == 2

    # 1. The nurse is not the teacher, police officer or clerk.
    model += nurse != teacher
    model += nurse != police_officer
    model += nurse != clerk
    # 2. The clerk is not the chef.
    model += clerk != chef
    # 3. Person 0 is not the boxer.
    model += boxer != 0
    # 4. Person 3 is not the teacher, police officer or nurse.
    model += teacher != 3
    model += police_officer != 3
    model += nurse != 3
    # 5. Person 0, the chef and the police officer are three different people.
    model += chef != 0
    model += police_officer != 0
    model += chef != police_officer

    return model, {
        "chef": chef, "guard": guard, "nurse": nurse, "clerk": clerk,
        "police_officer": police_officer, "teacher": teacher,
        "actor": actor, "boxer": boxer,
    }
