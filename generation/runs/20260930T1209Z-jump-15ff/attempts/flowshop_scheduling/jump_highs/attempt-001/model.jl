# Flow shop: every job goes through the machines in the same order. Choose the
# order of the jobs so that all of them are finished as early as possible.
using JuMP

function build(instance)
    time = instance["process_time"]    # time[j][m] = time of job j on machine m
    nj = length(instance["jobs"])
    nm = length(instance["machines"])
    horizon = sum(sum(row) for row in time)
    model = Model()
    # at[j, k] = 1 when job j is processed k-th
    @variable(model, at[1:nj, 1:nj], Bin)
    @constraint(model, [j = 1:nj], sum(at[j, :]) == 1)
    @constraint(model, [k = 1:nj], sum(at[:, k]) == 1)
    # the time of the k-th job on machine m, and its completion time there
    duration(k, m) = sum(time[j][m] * at[j, k] for j in 1:nj)
    @variable(model, 0 <= finish[1:nj, 1:nm] <= horizon, Int)
    for k in 1:nj, m in 1:nm
        @constraint(model, finish[k, m] >= duration(k, m))
        # a job reaches machine m after finishing on m - 1, and the machine takes
        # it after finishing the previous job
        m > 1 && @constraint(model, finish[k, m] >= finish[k, m - 1] + duration(k, m))
        k > 1 && @constraint(model, finish[k, m] >= finish[k - 1, m] + duration(k, m))
    end
    @variable(model, 0 <= makespan <= horizon, Int)
    @constraint(model, makespan >= finish[nj, nm])
    @objective(model, Min, makespan)
    return model, Dict("makespan" => makespan)
end
