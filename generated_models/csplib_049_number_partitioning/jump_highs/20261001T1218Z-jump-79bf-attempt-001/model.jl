# Number partitioning: split the numbers 1..n into two sets A and B of the same size
# with equal sums and equal sums of squares (n is even).
using JuMP

function build(instance)
    n = instance["n"]    # the numbers are 1..n
    half = div(n, 2)     # size of each set

    model = Model()

    # place[i, v] = 1 when position i holds the number v. Positions 1..half are the
    # entries of A and positions half+1..n are the entries of B. All n entries are
    # different numbers from 1..n, so each position holds one number and each number is used once.
    @variable(model, place[1:n, 1:n], Bin)
    @constraint(model, [i = 1:n], sum(place[i, v] for v in 1:n) == 1)
    @constraint(model, [v = 1:n], sum(place[i, v] for i in 1:n) == 1)

    # the numbers in position i (A for the first half, B for the second half)
    value(i) = sum(v * place[i, v] for v in 1:n)
    A = [value(i) for i in 1:half]
    B = [value(half + i) for i in 1:half]

    # the sum of the numbers in A equals the sum in B
    @constraint(model, sum(A) == sum(B))
    # the sum of the squares of the numbers in A equals the sum in B
    square(i) = sum(v^2 * place[i, v] for v in 1:n)
    @constraint(model, sum(square(i) for i in 1:half) == sum(square(half + i) for i in 1:half))

    return model, Dict("A" => A, "B" => B)
end
