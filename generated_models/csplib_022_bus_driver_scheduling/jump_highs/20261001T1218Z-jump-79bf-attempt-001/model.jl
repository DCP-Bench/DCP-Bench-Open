# Bus driver scheduling: given pieces of work to cover and a set of possible shifts, each
# covering some of the pieces, choose shifts so that every piece of work is covered by
# exactly one chosen shift, using as few shifts as possible (all shifts cost the same).
using JuMP

function build(instance)
    num_work = instance["num_work"]     # number of pieces of work, numbered 0..num_work-1
    num_shifts = instance["num_shifts"] # number of possible shifts
    shifts = instance["shifts"]         # shifts[i] = the pieces of work shift i covers

    model = Model()

    # x[i] = 1 when shift i is selected (declared output)
    @variable(model, x[1:num_shifts], Bin)

    # Every piece of work is covered by exactly one selected shift (set partitioning)
    for t in 0:num_work-1
        covering = [x[i] for i in 1:num_shifts if t in shifts[i]]
        @constraint(model, sum(covering) == 1)
    end

    # Use as few shifts as possible
    @objective(model, Min, sum(x))

    return model, Dict("x" => x)
end
