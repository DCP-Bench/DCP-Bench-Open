# Five brigands share 200 doubloons, each at least one, and the total would
# still be 200 if Alfonso had twelve times as much, Benito three times, Carlos
# the same, Diego half and Esteban a third.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    model = Model()
    @variable(model, 1 <= s[1:5] <= 200, Int)
    a, b, c, d, e = s
    @constraint(model, a + b + c + d + e == 200)
    # 12 * A + 3 * B + C + D/2 + E/3 = 200, multiplied by 6
    @constraint(model, 72 * a + 18 * b + 6 * c + 3 * d + 2 * e == 1200)
    return model, Dict("A" => a, "B" => b, "C" => c, "D" => d, "E" => e)
end
