# Low autocorrelation binary sequences: choose a sequence S of n values, each +1
# or -1, minimising the sum over k = 1..n-1 of the squared periodic
# autocorrelation C_k = sum_i S_i * S_((i + k) mod n).
using JuMP

function build(instance)
    n = instance["n"]   # length of the sequence
    model = Model()

    # bit[i] = 1 when S_i = +1 and 0 when S_i = -1, so S_i = 2 * bit[i] - 1
    @variable(model, bit[1:n], Bin)

    # differ[i, j] = 1 when S_i and S_j have different signs (an exclusive or of the
    # two bits, exact in all four cases). Then S_i * S_j = 1 - 2 * differ[i, j].
    differ = Dict{Tuple{Int,Int},VariableRef}()
    for i in 1:n-1, j in i+1:n
        d = @variable(model, binary = true)
        @constraint(model, d >= bit[i] - bit[j])
        @constraint(model, d >= bit[j] - bit[i])
        @constraint(model, d <= bit[i] + bit[j])
        @constraint(model, d <= 2 - bit[i] - bit[j])
        differ[(i, j)] = d
    end

    # partner(i, k) = the position (i + k) mod n, in 1-based numbering
    partner(i, k) = mod(i - 1 + k, n) + 1

    # For each shift k, the number of pairs (i, i + k mod n) with different signs is
    # n_diff[k] in 0..n, and then C_k = n - 2 * n_diff[k]. Only C_k squared is needed,
    # so n_diff[k] is written as a table lookup: is_count[k, v] = 1 when n_diff[k] = v
    # and C_k^2 = sum (n - 2v)^2 is_count[k, v] is then linear.
    @variable(model, is_count[1:n-1, 0:n], Bin)
    @constraint(model, [k = 1:n-1], sum(is_count[k, :]) == 1)
    @constraint(model, [k = 1:n-1],
                sum(v * is_count[k, v] for v in 0:n) ==
                sum(differ[(min(i, partner(i, k)), max(i, partner(i, k)))] for i in 1:n))

    # minimise the sum of the squared autocorrelations
    @objective(model, Min, sum((n - 2v)^2 * is_count[k, v] for k in 1:n-1, v in 0:n))

    # the sequence of +1 / -1 values (0 is excluded, as every bit is 0 or 1)
    sequence = [2 * bit[i] - 1 for i in 1:n]
    return model, Dict("sequence" => sequence)
end
