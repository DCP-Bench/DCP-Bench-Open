using JuMP, HiGHS, JSON

function solved(model)
    set_optimizer(model, HiGHS.Optimizer); set_silent(model)
    optimize!(model)
    return termination_status(model)
end

function try_case(name, f)
    try
        println(name, ": ", f())
    catch err
        println(name, ": ERROR ", sprint(showerror, err)[1:min(end, 300)])
    end
end

try_case("alldifferent", () -> begin
    m = Model(); @variable(m, 1 <= x[1:3] <= 3, Int)
    @constraint(m, x in MOI.AllDifferent(3)); @constraint(m, x[1] >= x[2] + 1)
    (solved(m), value.(x))
end)
try_case("alldifferent_unbounded", () -> begin
    m = Model(); @variable(m, x[1:3], Int)
    @constraint(m, x in MOI.AllDifferent(3))
    solved(m)
end)
try_case("table", () -> begin
    m = Model(); @variable(m, 0 <= x[1:2] <= 3, Int)
    @constraint(m, x in MOI.Table([1.0 2.0; 2.0 3.0])); @objective(m, Max, x[1])
    (solved(m), value.(x))
end)
try_case("circuit", () -> begin
    m = Model(); @variable(m, 1 <= x[1:4] <= 4, Int)
    @constraint(m, x in MOI.Circuit(4)); @constraint(m, x[1] == 3)
    (solved(m), value.(x))
end)
try_case("count_distinct", () -> begin
    m = Model(); @variable(m, 1 <= x[1:4] <= 3, Int); @variable(m, 0 <= k <= 4, Int)
    @constraint(m, [k; x] in MOI.CountDistinct(5)); @objective(m, Max, k)
    (solved(m), value(k))
end)
try_case("count_belongs", () -> begin
    m = Model(); @variable(m, 0 <= x[1:4] <= 3, Int); @variable(m, 0 <= k <= 4, Int)
    @constraint(m, [k; x] in MOI.CountBelongs(5, Set([2]))); @constraint(m, k == 3)
    (solved(m), value.(x))
end)
try_case("indicator", () -> begin
    m = Model(); @variable(m, b, Bin); @variable(m, 0 <= x <= 10, Int)
    @constraint(m, b --> {x <= 3}); @constraint(m, b == 1); @objective(m, Max, x)
    (solved(m), value(x))
end)
try_case("indicator_negated", () -> begin
    m = Model(); @variable(m, b, Bin); @variable(m, 0 <= x <= 10, Int)
    @constraint(m, !b --> {x >= 7}); @constraint(m, b == 0); @objective(m, Min, x)
    (solved(m), value(x))
end)
try_case("reified", () -> begin
    m = Model(); @variable(m, b, Bin); @variable(m, 0 <= x <= 10, Int)
    @constraint(m, [b, x] in MOI.Reified(MOI.LessThan(3.0))); @constraint(m, x == 2)
    (solved(m), value(b))
end)
try_case("quadratic_binaries", () -> begin
    m = Model(); @variable(m, a, Bin); @variable(m, b, Bin)
    @constraint(m, a * b == 1)
    solved(m)
end)
try_case("sos1", () -> begin
    m = Model(); @variable(m, 0 <= x[1:3] <= 1)
    @constraint(m, x in SOS1([1, 2, 3])); @objective(m, Max, sum(x))
    (solved(m), objective_value(m))
end)
try_case("json_shapes", () -> begin
    d = JSON.parse("{\"m\": [[1, 2], [3, 4]], \"s\": \"ab\", \"b\": true, \"o\": {\"k\": 1}}"; dicttype = Dict{String, Any})
    rows = d["m"]
    M = permutedims(reduce(hcat, rows))
    (typeof(d), typeof(rows), rows[2][1], M[2, 1], size(M), typeof(d["s"]), d["b"], typeof(d["o"]))
end)
try_case("sum_vector_any", () -> begin
    d = JSON.parse("{\"w\": [3, 5, 2]}"; dicttype = Dict{String, Any})
    m = Model(); @variable(m, x[1:3], Bin)
    @constraint(m, sum(d["w"][i] * x[i] for i in 1:3) == 5)
    (solved(m), value.(x))
end)
try_case("objective_value_int", () -> begin
    m = Model(); @variable(m, 0 <= x <= 7, Int); @objective(m, Max, 3x)
    (solved(m), objective_value(m), relative_gap(m))
end)
