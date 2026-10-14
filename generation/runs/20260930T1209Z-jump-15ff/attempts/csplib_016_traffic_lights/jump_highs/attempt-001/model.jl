# Traffic lights: four vehicle lights V1..V4 and four pedestrian lights P1..P4 at
# a junction. Each (V_i, P_i, V_i+1, P_i+1), going round the junction, must be
# one of the allowed combinations.
using JuMP

function build(instance)
    allowed = instance["allowed_tuples"]
    # the allowed combinations as a Float64 matrix, one per row, as MOI.Table wants
    tuples = Float64[allowed[t][k] for t in 1:length(allowed), k in 1:4]
    model = Model()
    @variable(model, 0 <= vehicle[1:4] <= 3, Int)     # 0 red, 1 red-yellow, 2 green, 3 yellow
    @variable(model, 0 <= pedestrian[1:4] <= 1, Int)  # 0 red, 1 green
    for i in 1:4
        nxt = mod1(i + 1, 4)
        @constraint(model, [vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]] in MOI.Table(tuples))
    end
    return model, Dict("lights" => vcat(vehicle, pedestrian))
end
