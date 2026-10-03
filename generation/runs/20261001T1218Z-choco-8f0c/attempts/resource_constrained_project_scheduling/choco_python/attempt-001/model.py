# Resource-constrained project scheduling: schedule jobs with given durations, respecting
# precedence constraints between jobs and the capacity of every renewable resource at
# every time, so that the makespan (the latest start time) is as small as possible.
from pychoco.model import Model


def build(instance):
    durations = instance["durations_data"]  # durations[j] = duration of job j
    resource_needs = instance["resource_needs_data"]  # resource_needs[j][r] = units of resource r job j uses
    resource_capacities = instance["resource_capacities_data"]  # units available of each resource
    successors_link = instance["successors_link_data"]  # pairs [i, j]: job j starts after job i ends
    nb_jobs = len(durations)
    nb_resource = len(resource_capacities)

    # no job can start later than the time at which all jobs run one after the other
    max_duration = sum(durations)

    model = Model()

    # start_time[j] = start time of job j
    start_time = [model.intvar(0, max_duration, name=f"start_{j}") for j in range(nb_jobs)]

    # precedence: job j starts no earlier than job i ends, for every pair [i, j]
    for i, j in successors_link:
        model.arithm(start_time[i], "-", start_time[j], "<=", -durations[i]).post()

    # resource capacity: at any time the jobs running together use at most the capacity of
    # each resource. Jobs with zero duration or zero need of a resource cannot matter
    # for that resource, so they are left out of its cumulative constraint.
    tasks = [model.task(start_time[j], durations[j]) for j in range(nb_jobs)]
    for r in range(nb_resource):
        users = [j for j in range(nb_jobs) if durations[j] > 0 and resource_needs[j][r] > 0]
        if not users:
            continue
        model.cumulative([tasks[j] for j in users],
                         [model.intvar(resource_needs[j][r], resource_needs[j][r]) for j in users],
                         model.intvar(resource_capacities[r], resource_capacities[r])).post()

    # makespan: the latest start time (the last job is a dummy of duration 0)
    makespan = model.intvar(0, max_duration, name="makespan")
    model.max(makespan, start_time).post()

    return model, {"start_time": start_time}, ("minimize", makespan)
