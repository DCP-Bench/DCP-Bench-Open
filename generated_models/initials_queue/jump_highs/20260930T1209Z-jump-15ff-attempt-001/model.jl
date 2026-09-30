# Initials queue: the ten people in a queue have as initials the ten different
# alphabetically ordered pairs of distinct letters from A-E, no one shares a
# letter with the person in front, BE is first, CD second and BD last.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 10
    pairs = [(a, b) for a in 0:4 for b in a+1:4]   # the ten possible initials, A..E as 0..4
    model = Model()
    # has[i, p] = 1 when person i has the initials pairs[p]
    @variable(model, has[1:n, 1:length(pairs)], Bin)
    @constraint(model, [i = 1:n], sum(has[i, :]) == 1)
    @constraint(model, [p = 1:length(pairs)], sum(has[:, p]) == 1)   # nobody shares initials
    # nobody shares a letter with the person in front
    for i in 1:n-1, p in 1:length(pairs), q in 1:length(pairs)
        if !isempty(intersect(pairs[p], pairs[q]))
            @constraint(model, has[i, p] + has[i + 1, q] <= 1)
        end
    end
    # BE is at the front, CD right behind, BD at the end
    fix(has[1, findfirst(==((1, 4)), pairs)], 1; force = true)
    fix(has[2, findfirst(==((2, 3)), pairs)], 1; force = true)
    fix(has[n, findfirst(==((1, 3)), pairs)], 1; force = true)
    @variable(model, 0 <= queue[1:n, 1:2] <= 4, Int)
    @constraint(model, [i = 1:n, k = 1:2], queue[i, k] == sum(pairs[p][k] * has[i, p] for p in 1:length(pairs)))
    return model, Dict("queue" => queue)
end
