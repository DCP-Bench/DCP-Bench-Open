# ISBN-13: fill in the unknown digits (-1) so that the number starts with 978 or
# 979 and its last digit is (10 - (s mod 10)) mod 10, where s weights the first
# twelve digits alternately by 1 and 3.
using JuMP

function build(instance)
    init = instance["isbn_init"]
    n = 13
    model = Model()
    @variable(model, 0 <= isbn[1:n] <= 9, Int)
    for i in 1:n
        init[i] != -1 && fix(isbn[i], init[i]; force = true)
    end
    # the prefix is 978 or 979
    @constraint(model, isbn[1] == 9)
    @constraint(model, isbn[2] == 7)
    @constraint(model, 8 <= isbn[3] <= 9)
    # s = 10 q + r with 0 <= r <= 9, and the check digit is (10 - r) mod 10:
    # 0 when r = 0, 10 - r otherwise
    weights = [isodd(i) ? 1 : 3 for i in 1:n-1]
    @variable(model, 0 <= q <= 30, Int)
    @variable(model, 0 <= r <= 9, Int)
    @constraint(model, sum(weights[i] * isbn[i] for i in 1:n-1) == 10 * q + r)
    @variable(model, zero_rest, Bin)
    @constraint(model, zero_rest --> {r == 0})
    @constraint(model, !zero_rest --> {r >= 1})
    @constraint(model, zero_rest --> {isbn[n] == 0})
    @constraint(model, !zero_rest --> {isbn[n] == 10 - r})
    return model, Dict("isbn" => isbn)
end
