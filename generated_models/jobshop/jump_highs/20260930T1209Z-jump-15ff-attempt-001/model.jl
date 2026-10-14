# Job shop: each job is a sequence of tasks, each on a given machine for a given
# time; a job's tasks run in order, a machine runs one task at a time, and the
# schedule is as short as possible.
using JuMP

function build(instance)
    jobs = instance["jobs_data"]     # per job, its tasks as [machine, duration]
    horizon = sum(task[2] for job in jobs for task in job)
    tasks = [(j, t) for j in 1:length(jobs) for t in 1:length(jobs[j])]
    model = Model()
    @variable(model, 0 <= start[tasks] <= horizon, Int)
    duration(jt) = jobs[jt[1]][jt[2]][2]
    machine(jt) = jobs[jt[1]][jt[2]][1]
    # the tasks of a job run in order
    for (j, t) in tasks
        t > 1 && @constraint(model, start[(j, t)] >= start[(j, t - 1)] + duration((j, t - 1)))
    end
    # a machine runs one task at a time: for two tasks on it, one precedes the other
    for a in tasks, b in tasks
        if a < b && machine(a) == machine(b)
            first = @variable(model, binary = true)
            @constraint(model, start[a] + duration(a) <= start[b] + horizon * (1 - first))
            @constraint(model, start[b] + duration(b) <= start[a] + horizon * first)
        end
    end
    @variable(model, 0 <= makespan <= horizon, Int)
    @constraint(model, [jt in tasks], start[jt] + duration(jt) <= makespan)
    @objective(model, Min, makespan)
    return model, Dict("makespan" => makespan)
end
