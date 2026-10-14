# Quasigroup existence, QG3.m: an order m quasigroup is an m x m multiplication table in
# which every element occurs once in each row and each column (a Latin square). QG3.m
# asks in addition for (a * b) * (b * a) = a for all elements a and b.
using JuMP

function build(instance)
    m = instance["m"]   # order of the quasigroup; elements are 0..m-1

    model = Model()

    # table[a, b, v] = 1 when a * b = v (elements numbered 0..m-1)
    @variable(model, table[0:m-1, 0:m-1, 0:m-1], Bin)

    # each product a * b is one element
    @constraint(model, [a = 0:m-1, b = 0:m-1], sum(table[a, b, v] for v in 0:m-1) == 1)
    # each element occurs once in every row a
    @constraint(model, [a = 0:m-1, v = 0:m-1], sum(table[a, b, v] for b in 0:m-1) == 1)
    # each element occurs once in every column b
    @constraint(model, [b = 0:m-1, v = 0:m-1], sum(table[a, b, v] for a in 0:m-1) == 1)

    # QG3.m property (a * b) * (b * a) = a. Write c = a * b and d = b * a: whenever the table
    # holds c at (a, b) and d at (b, a), it must hold a at (c, d).
    for a in 0:m-1, b in 0:m-1, c in 0:m-1, d in 0:m-1
        @constraint(model, table[a, b, c] + table[b, a, d] <= 1 + table[c, d, a])
    end

    # quasigroup[a][b] = the product a * b (declared output)
    quasigroup = [sum(v * table[a, b, v] for v in 0:m-1) for a in 0:m-1, b in 0:m-1]
    return model, Dict("quasigroup" => quasigroup)
end
