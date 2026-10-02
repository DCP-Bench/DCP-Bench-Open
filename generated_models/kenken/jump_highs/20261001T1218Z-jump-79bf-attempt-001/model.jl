# KenKen: fill an n x n grid with the digits 1..n so that every row and every column holds
# each digit once, and each cage (a group of cells) achieves its target number using
# addition, subtraction, multiplication or division. Digits may repeat inside a cage.
using JuMP

# The digit tuples that satisfy a cage with target `res` and `len` cells. A cage of two
# cells may combine its digits by sum, product, difference or quotient (either order);
# any other cage (one cell, or three or more) has digits adding up to or multiplying to
# the target.
function cage_tuples(res, len, n)
    allowed = Vector{Vector{Int}}()
    for t in Iterators.product(ntuple(_ -> 1:n, len)...)
        digits = collect(t)
        if len == 2
            a, b = digits
            ok = a + b == res || a * b == res || a * res == b || b * res == a ||
                 a - b == res || b - a == res
        else
            ok = sum(digits) == res || prod(digits) == res
        end
        ok && push!(allowed, digits)
    end
    return allowed
end

function build(instance)
    n = instance["n"]               # size of the grid and largest digit
    cages = instance["problem"]     # each cage is [target, [[row, col], ...]], 1-based cells

    model = Model()

    # digit[i, j, d] = 1 when cell (i, j) holds the digit d; every cell holds one digit
    @variable(model, digit[1:n, 1:n, 1:n], Bin)
    @constraint(model, [i = 1:n, j = 1:n], sum(digit[i, j, d] for d in 1:n) == 1)

    # each row holds each digit exactly once
    @constraint(model, [i = 1:n, d = 1:n], sum(digit[i, j, d] for j in 1:n) == 1)
    # each column holds each digit exactly once
    @constraint(model, [j = 1:n, d = 1:n], sum(digit[i, j, d] for i in 1:n) == 1)

    # Cages: a cage takes exactly one of the digit tuples that reach its target, and each
    # of its cells then holds the digit that tuple gives it.
    for (res, cells) in cages
        tuples = cage_tuples(res, length(cells), n)
        pick = @variable(model, [1:length(tuples)], Bin)
        @constraint(model, sum(pick) == 1)
        for (pos, cell) in enumerate(cells), d in 1:n
            @constraint(model, digit[cell[1], cell[2], d] ==
                               sum(pick[t] for t in 1:length(tuples) if tuples[t][pos] == d; init = 0))
        end
    end

    # x[i, j] = the digit in cell (i, j) (declared output)
    x = [sum(d * digit[i, j, d] for d in 1:n) for i in 1:n, j in 1:n]
    return model, Dict("x" => x)
end
