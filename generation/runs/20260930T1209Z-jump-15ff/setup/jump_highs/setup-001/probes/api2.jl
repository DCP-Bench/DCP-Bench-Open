using JuMP, HiGHS

function try_case(name, f)
    try
        println(name, ": ", f())
    catch err
        println(name, ": ERROR ", first(sprint(showerror, err), 200))
    end
end

solved(m) = (set_optimizer(m, HiGHS.Optimizer); set_silent(m); optimize!(m); termination_status(m))

try_case("table_int_matrix", () -> begin
    m = Model(); @variable(m, 0 <= x[1:2] <= 3, Int)
    @constraint(m, x in MOI.Table([1 2; 2 3])); @objective(m, Max, x[1])
    (solved(m), value.(x))
end)
try_case("name_reuse", () -> begin
    m = Model()
    for i in 1:2
        @variable(m, helper, Bin)
    end
    "no error"
end)
try_case("anonymous_in_loop", () -> begin
    m = Model()
    hs = [@variable(m, [1:3], Bin) for i in 1:2]
    (length(hs), length(hs[1]))
end)
function loop_scope()
    total = 0
    for i in 1:3
        total += i
        inner = i
    end
    return (total, @isdefined(inner))
end
try_case("loop_scope", loop_scope)
try_case("set_attribute_without_optimizer", () -> begin
    m = Model(); set_attribute(m, "presolve", "off"); "no error"
end)
try_case("expression_macro", () -> begin
    m = Model(); @variable(m, 0 <= x[1:3] <= 2, Int)
    @expression(m, total, sum(x)); @constraint(m, total == 5)
    (solved(m), value(total))
end)
