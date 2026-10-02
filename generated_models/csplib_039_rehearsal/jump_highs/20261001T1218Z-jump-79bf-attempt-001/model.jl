# Rehearsal problem: order the pieces of a concert for rehearsal. A player arrives just
# before the first piece they play in and leaves just after the last one; minimise the
# total time that players are present but not playing.
using JuMP

function build(instance)
    n = instance["num_pieces"]
    P = instance["num_players"]
    duration = instance["duration"]       # duration[k] = rehearsal time of piece k
    rehearsal = instance["rehearsal"]     # rehearsal[p][k] = 1 when player p plays in piece k

    model = Model()

    # at[k, i] = 1 when piece k (numbered from 1 here) is rehearsed in slot i; every slot
    # holds one piece and every piece is rehearsed once (a permutation).
    @variable(model, at[1:n, 1:n], Bin)
    @constraint(model, [i = 1:n], sum(at[k, i] for k in 1:n) == 1)
    @constraint(model, [k = 1:n], sum(at[k, i] for i in 1:n) == 1)

    # plays[p, i] = 1 when player p plays in the piece rehearsed in slot i
    plays = [sum(rehearsal[p][k] * at[k, i] for k in 1:n) for p in 1:P, i in 1:n]

    # arrived[p, i] = 1 when player p has played in some slot up to i, and stays = 1 when
    # p still plays in some slot from i on. Only lower bounds are needed: the objective
    # is minimised, so the solver sets them as small as the bounds allow, which is exact.
    @variable(model, 0 <= arrived[1:P, 1:n] <= 1)
    @variable(model, 0 <= stays[1:P, 1:n] <= 1)
    @constraint(model, [p = 1:P, i = 1:n], arrived[p, i] >= plays[p, i])
    @constraint(model, [p = 1:P, i = 1:n], stays[p, i] >= plays[p, i])
    @constraint(model, [p = 1:P, i = 2:n], arrived[p, i] >= arrived[p, i-1])
    @constraint(model, [p = 1:P, i = 1:n-1], stays[p, i] >= stays[p, i+1])

    # present[p, i] = 1 when player p is at the rehearsal in slot i: after arriving and
    # before leaving
    @variable(model, 0 <= present[1:P, 1:n] <= 1)
    @constraint(model, [p = 1:P, i = 1:n], present[p, i] >= arrived[p, i] + stays[p, i] - 1)

    # waiting[p, i, k] = 1 when player p is present in slot i, piece k is rehearsed there and
    # p does not play in k. Only pieces k that p does not play in can make p wait.
    @variable(model, 0 <= waiting[p = 1:P, i = 1:n, k = 1:n] <= 1)
    for p in 1:P, i in 1:n, k in 1:n
        if rehearsal[p][k] == 0
            @constraint(model, waiting[p, i, k] >= present[p, i] + at[k, i] - 1)
        else
            @constraint(model, waiting[p, i, k] == 0)
        end
    end

    # Minimise the total waiting time: the duration of the piece in the slot, for each
    # player that is present and not playing.
    @objective(model, Min, sum(duration[k] * waiting[p, i, k] for p in 1:P, i in 1:n, k in 1:n))

    # rehearsal_order[i] = the piece rehearsed in slot i (declared output, pieces from 0)
    rehearsal_order = [sum((k - 1) * at[k, i] for k in 1:n) for i in 1:n]
    return model, Dict("rehearsal_order" => rehearsal_order)
end
