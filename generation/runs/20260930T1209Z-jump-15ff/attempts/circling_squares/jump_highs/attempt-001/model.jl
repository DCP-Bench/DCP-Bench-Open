# Circling the squares: different numbers 1..99 in ten squares round a circle so
# that the squares of any two adjacent numbers add up to the squares of the two
# opposite them. A, B, F and G are given.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]
    model = Model()
    # is[s, v] = 1 when square s holds v
    @variable(model, is[1:10, 1:99], Bin)
    @constraint(model, [s = 1:10], sum(is[s, :]) == 1)
    @constraint(model, [v = 1:99], sum(is[:, v]) <= 1)   # all different
    @variable(model, 1 <= x[1:10] <= 99, Int)
    @constraint(model, [s = 1:10], x[s] == sum(v * is[s, v] for v in 1:99))
    sq = [sum(v^2 * is[s, v] for v in 1:99) for s in 1:10]
    A, B, C, D, E, F, G, H, I, K = 1:10
    for (s, v) in ((A, 16), (B, 2), (F, 8), (G, 14))
        fix(is[s, v], 1; force = true)
    end
    @constraint(model, sq[A] + sq[B] == sq[F] + sq[G])
    @constraint(model, sq[B] + sq[C] == sq[G] + sq[H])
    @constraint(model, sq[C] + sq[D] == sq[H] + sq[I])
    @constraint(model, sq[D] + sq[E] == sq[I] + sq[K])
    @constraint(model, sq[E] + sq[F] == sq[K] + sq[A])
    return model, Dict(names[s] => x[s] for s in 1:10)
end
