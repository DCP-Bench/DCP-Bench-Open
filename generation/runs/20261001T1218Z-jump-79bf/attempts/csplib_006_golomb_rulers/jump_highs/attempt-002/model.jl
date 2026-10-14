# Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... < a_m on a
# ruler so that all pairwise differences a_j - a_i are distinct; minimise the length a_m.
using JuMP

function build(instance)
    m = instance["size"]     # number of marks on the ruler
    L = m * m                # largest position a mark may take (the reference's domain bound)

    model = Model()

    # marks[k] = position of the k-th mark. Mark k has k-1 marks before it and m-k after
    # it, each at least one unit apart, which gives the bounds below.
    @variable(model, k - 1 <= marks[k = 1:m] <= L - (m - k), Int)
    # ruler_length = position of the last mark (declared output, kept as its own variable)
    @variable(model, 0 <= ruler_length <= L, Int)

    # the first mark is at 0
    @constraint(model, marks[1] == 0)
    # marks are strictly increasing
    @constraint(model, [k = 1:m-1], marks[k] + 1 <= marks[k+1])
    @constraint(model, ruler_length == marks[m])

    # Golomb condition: the m(m-1)/2 differences a_j - a_i (i < j) are pairwise distinct.
    pairs = [(i, j) for i in 1:m-1 for j in i+1:m]
    # The marks i..j carry (j-i+1)(j-i)/2 distinct positive differences, and a_j - a_i is
    # the largest of them, so a_j - a_i >= (j-i+1)(j-i)/2. The upper end follows from
    # the other marks each taking at least one unit of the ruler.
    lo(i, j) = div((j - i + 1) * (j - i), 2)
    hi(i, j) = L - (m - 1 - (j - i))
    # is_diff[p][v] = 1 when the difference of pair p equals v (one value per pair)
    is_diff = [@variable(model, [lo(i, j):hi(i, j)], Bin) for (i, j) in pairs]
    for (p, (i, j)) in enumerate(pairs)
        @constraint(model, sum(is_diff[p]) == 1)
        @constraint(model, marks[j] - marks[i] == sum(v * is_diff[p][v] for v in lo(i, j):hi(i, j)))
    end
    # each difference value is taken by at most one pair
    for v in 1:L
        users = [is_diff[p][v] for (p, (i, j)) in enumerate(pairs) if lo(i, j) <= v <= hi(i, j)]
        if length(users) > 1
            @constraint(model, sum(users) <= 1)
        end
    end

    # Implied cuts that only strengthen the LP relaxation. The differences among any r
    # consecutive marks i..j are n = r(r-1)/2 distinct positive integers, so they add up
    # to at least 1 + 2 + ... + n = n(n+1)/2. Their sum is sum_k (2(k-i+1) - r - 1) * a_k.
    for i in 1:m-2, j in i+2:m
        r = j - i + 1
        n = div(r * (r - 1), 2)
        @constraint(model, sum((2 * (k - i + 1) - r - 1) * marks[k] for k in i:j) >= div(n * (n + 1), 2))
    end

    # find the shortest ruler
    @objective(model, Min, ruler_length)

    return model, Dict("marks" => marks, "length" => ruler_length)
end
