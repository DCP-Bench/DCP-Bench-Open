The resource-constrained project scheduling problem involves scheduling a set of jobs, each with a specific
duration and resource requirement, such that the total project duration (makespan) is minimized. Each job may have
precedence constraints, meaning certain jobs must be completed before others can start. Additionally,
there are multiple types of resources, each with a limited capacity that must not be exceeded at any time.

Given the durations of the jobs, their resource requirements, the capacities of the resources, and the precedence
constraints between the jobs, determine the start times of the jobs that minimize the makespan while satisfying all
constraints.

Print the start times of the jobs (start_time) as a list of integers starting from 0.
