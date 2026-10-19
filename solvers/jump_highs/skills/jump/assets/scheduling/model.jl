# Scheduling: jobs visit machines in order; two operations on one machine must not overlap.
using JuMP, HiGHS

# jobs[j][k] = (machine, duration) of the k-th operation of job j. Jobs may have different lengths.
jobs = [[(1, 3), (2, 2)], [(2, 4), (1, 2), (2, 1)]]
n_jobs = length(jobs)
n_ops(j) = length(jobs[j])                       # per-job length, never length(jobs[1])
machine(j, k) = jobs[j][k][1]
duration(j, k) = jobs[j][k][2]
horizon = sum(duration(j, k) for j in 1:n_jobs for k in 1:n_ops(j))   # big-M: all work in sequence

model = Model(HiGHS.Optimizer)
set_silent(model)

start = [@variable(model, [1:n_ops(j)], lower_bound = 0, upper_bound = horizon) for j in 1:n_jobs]
@variable(model, makespan >= 0)

# Operations of a job run in order, and end before the makespan.
for j in 1:n_jobs, k in 1:n_ops(j)
    @constraint(model, makespan >= start[j][k] + duration(j, k))
    if k > 1
        @constraint(model, start[j][k] >= start[j][k-1] + duration(j, k-1))
    end
end

# Operations on the same machine: a binary picks which one goes first.
cells = [(j, k) for j in 1:n_jobs for k in 1:n_ops(j)]
for p in eachindex(cells), q in (p+1):length(cells)
    j1, k1 = cells[p]
    j2, k2 = cells[q]
    if machine(j1, k1) == machine(j2, k2)
        before = @variable(model, binary = true)
        @constraint(model, start[j1][k1] + duration(j1, k1) <= start[j2][k2] + horizon * (1 - before))
        @constraint(model, start[j2][k2] + duration(j2, k2) <= start[j1][k1] + horizon * before)
    end
end

@objective(model, Min, makespan)
optimize!(model)
println("Status: ", termination_status(model))
println("Makespan: ", round(Int, objective_value(model)))
