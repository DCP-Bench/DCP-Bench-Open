from ortools.sat.python import cp_model


def build(instance):
    """Jobs puzzle: four people hold eight jobs, two each.

    The puzzle states its own people, jobs and clues, so `instance` is unused.
    Each variable holds the index of the person doing that job.
    """
    del instance

    num_people = 4
    num_jobs = 8

    model = cp_model.CpModel()
    jobs = [model.new_int_var(0, num_people - 1, f"job{j}") for j in range(num_jobs)]
    chef, guard, nurse, clerk, police_officer, teacher, actor, boxer = jobs

    # Each person holds exactly two jobs.
    for i in range(num_people):
        held = []
        for j in range(num_jobs):
            does = model.new_bool_var(f"does{i}_{j}")
            model.add(jobs[j] == i).only_enforce_if(does)
            model.add(jobs[j] != i).only_enforce_if(~does)
            held.append(does)
        model.add(sum(held) == 2)

    # 1. The nurse is not the teacher, police officer or clerk.
    model.add(nurse != teacher)
    model.add(nurse != police_officer)
    model.add(nurse != clerk)
    # 2. The clerk is not the chef.
    model.add(clerk != chef)
    # 3. Person 0 is not the boxer.
    model.add(boxer != 0)
    # 4. Person 3 is not the teacher, police officer or nurse.
    model.add(teacher != 3)
    model.add(police_officer != 3)
    model.add(nurse != 3)
    # 5. Person 0, the chef and the police officer are three different people.
    model.add(chef != 0)
    model.add(police_officer != 0)
    model.add(chef != police_officer)

    return model, {
        "chef": chef, "guard": guard, "nurse": nurse, "clerk": clerk,
        "police_officer": police_officer, "teacher": teacher,
        "actor": actor, "boxer": boxer,
    }
