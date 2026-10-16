from pycsp3 import *

durations = data.durations_data
needs = data.resource_needs_data
capacities = data.resource_capacities_data
precedences = data.successors_link_data
J = len(durations)  # the jobs, including the dummy source (first) and the dummy sink (last)
H = sum(durations)  # an upper bound on the makespan

# the start time of each job
start_time = VarArray(size=J, dom=range(H + 1))

satisfy(
    # the project starts at time 0
    start_time[0] == 0,
    # a job can only start after the jobs that must be completed before it
    [start_time[j] >= start_time[i] + durations[i] for i, j in precedences],
)

# at no time may the jobs using a resource exceed its capacity
satisfy(
    [Cumulative(origins=start_time, lengths=durations, heights=[needs[j][r] for j in range(J)]) <= capacities[r]
     for r in range(len(capacities))],
)

# the total project duration is as short as possible: the start of the last job is the makespan
minimize(start_time[J - 1])
