# Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... < a_m on a
# ruler so that all pairwise differences a_j - a_i are distinct; minimise the length a_m.
using JuMP

# A Golomb ruler with m marks built greedily: each new mark is the nearest position that
# keeps all differences distinct. Its length bounds the optimal length from above.
function greedy_length(m)
    marks = [0]
    used = Set{Int}()
    while length(marks) < m
        c = marks[end] + 1
        while any((c - a) in used for a in marks)
            c += 1
        end
        union!(used, [c - a for a in marks])
        push!(marks, c)
    end
    return marks[end]
end

function build(instance)
    m = instance["size"]     # number of marks on the ruler
    # Largest position a mark may take: the reference's bound m^2, or the length of the
    # greedy ruler when that is smaller (an optimal ruler is no longer than any ruler).
    L = min(m * m, greedy_length(m))

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

    # find the shortest ruler
    @objective(model, Min, ruler_length)

    return model, Dict("marks" => marks, "length" => ruler_length)
end
