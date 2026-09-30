# Solving side of the jump_highs integration. Runs inside the image only.
#
# `run.py` starts this driver as
#
#     julia driver.jl RECORD_FILE DEADLINE
#
# where DEADLINE is a Unix time. The driver includes the submission, calls its
# `build(instance)`, attaches HiGHS, solves, proves the optimum when there is an
# objective, enumerates distinct declared outputs, and writes the runner protocol
# as JSON lines to RECORD_FILE, flushing after each one. Standard output is left
# to the submission and to the solver; run.py relays it to stderr, so a stray
# println in a model cannot corrupt the protocol.
#
# A MIP solver returns one solution rather than a stream, so enumeration works by
# exclusion, as in the PuLP integration: the objective is pinned to the proven
# optimum, and each further solve adds a no-good cut over the integer variables
# the declared outputs are built from. That needs those variables to be integer
# and bounded, and the driver says so when they are not.

using JuMP
using HiGHS
using JSON

# HiGHS returns floats; a declared output has to be an integer, and anything
# further from one than this is a modelling error rather than solver noise.
const TOLERANCE = 1e-5

struct SubmissionError <: Exception
    message::String
end
Base.showerror(io::IO, e::SubmissionError) = print(io, e.message)

record(io, object) = (println(io, JSON.json(object)); flush(io))
status(io, name, detail = "") = record(io, Dict("type" => "status", "status" => name, "detail" => detail))

# ---------------------------------------------------------------------------
# The declared outputs

# Every leaf of the outputs, in order: numbers, strings, variables, expressions.
leaves(value::AbstractDict) = reduce(vcat, [leaves(v) for v in values(value)]; init = Any[])
leaves(value::Union{AbstractArray, Tuple}) = reduce(vcat, [leaves(v) for v in value]; init = Any[])
leaves(value::JuMP.Containers.DenseAxisArray) = leaves(value.data)
leaves(value) = Any[value]

# A matrix is written as its rows, and an n-dimensional array as nested lists
# indexed by its first dimension, which is how the references write them.
nested(value::AbstractVector) = collect(value)
nested(value::AbstractArray) = [nested(selectdim(value, 1, i)) for i in axes(value, 1)]

resolved(value::AbstractDict) = Dict(string(k) => resolved(v) for (k, v) in value)
resolved(value::AbstractArray) = [resolved(v) for v in nested(value)]
resolved(value::Tuple) = [resolved(v) for v in value]
resolved(value::JuMP.Containers.DenseAxisArray) = resolved(value.data)
resolved(value::JuMP.Containers.SparseAxisArray) =
    throw(SubmissionError("A declared output is a SparseAxisArray; give it as an array or a list"))
resolved(value::AbstractString) = String(value)
resolved(value::Bool) = value
resolved(value::Integer) = Int(value)
resolved(value::Real) = integral(value)
resolved(value::Union{VariableRef, GenericAffExpr}) = integral(JuMP.value(value))
resolved(value) = throw(SubmissionError("A declared output holds a $(typeof(value)), which is not a " *
                                        "number, a string, a variable, an expression or an array of them"))

function integral(value::Real)
    rounded = round(value)
    if abs(value - rounded) > TOLERANCE
        throw(SubmissionError("Declared outputs must be integers; got the fractional value $(value)"))
    end
    return Int(rounded)
end

# The variables a no-good cut has to move.
function cut_variables(outputs)
    found = VariableRef[]
    for leaf in leaves(outputs)
        if leaf isa VariableRef
            push!(found, leaf)
        elseif leaf isa GenericAffExpr
            append!(found, collect(keys(leaf.terms)))
        end
    end
    return unique(found)
end

bounds(v::VariableRef) =
    is_binary(v) ? (0, 1) :
    is_fixed(v) ? (fix_value(v), fix_value(v)) :
    (has_lower_bound(v) ? lower_bound(v) : nothing, has_upper_bound(v) ? upper_bound(v) : nothing)

# Why these variables cannot carry a no-good cut, or nothing if they can.
function obstacle(variables)
    for v in variables
        if !(is_binary(v) || is_integer(v))
            return "Enumeration needs integer declared outputs; $(name(v)) is continuous"
        end
        low, high = bounds(v)
        if low === nothing || high === nothing
            return "Enumeration needs bounded declared outputs; $(name(v)) has no finite lower and upper bound"
        end
    end
    return nothing
end

# Forbid the assignment `current` gives the variables. False when every variable
# is pinned to its only value, so no other assignment exists. JuMP refuses to
# report a solution once the model has changed, so the values are read first.
function forbid!(model, variables, current)
    indicators = VariableRef[]
    for (v, value) in zip(variables, current)
        low, high = round.(Int, bounds(v))
        if value > low
            below = @variable(model, binary = true)
            @constraint(model, v <= value - 1 + (high - value + 1) * (1 - below))
            push!(indicators, below)
        end
        if value < high
            above = @variable(model, binary = true)
            @constraint(model, v >= value + 1 - (value + 1 - low) * (1 - above))
            push!(indicators, above)
        end
    end
    isempty(indicators) && return false
    @constraint(model, sum(indicators) >= 1)
    return true
end

# ---------------------------------------------------------------------------
# Solving

# Solve once inside the remaining budget and say what HiGHS concluded. OPTIMAL is
# the only answer: HiGHS reports TIME_LIMIT for a feasible point it did not prove.
function attempt(model, deadline)
    left = deadline - time()
    left <= 0.5 && return :timeout
    set_time_limit_sec(model, left - 0.5)
    optimize!(model)
    code = termination_status(model)
    if code == OPTIMAL
        primal_status(model) == FEASIBLE_POINT && return :solved
        return :error
    elseif code in (INFEASIBLE, INFEASIBLE_OR_UNBOUNDED)
        return :infeasible
    elseif code == DUAL_INFEASIBLE
        return :unbounded
    elseif code == TIME_LIMIT
        return :timeout
    end
    throw(SubmissionError("HiGHS stopped with status $(code)"))
end

function load(instance)
    Base.include(Main, "/input/model.jl")
    # The submission's definitions are newer than this function, so they are
    # looked up and called in the latest world.
    if !Base.invokelatest(isdefined, Main, :build)
        throw(SubmissionError("The submission defines no build(instance) function"))
    end
    build = Base.invokelatest(getglobal, Main, :build)
    returned = Base.invokelatest(build, instance)
    if !(returned isa Tuple && length(returned) == 2)
        throw(SubmissionError("build(instance) must return (model, outputs)"))
    end
    model, outputs = returned
    model isa JuMP.Model || throw(SubmissionError("The first value build returns must be a JuMP.Model"))
    if !(outputs isa AbstractDict) || isempty(outputs)
        throw(SubmissionError("The second value build returns must be a nonempty Dict of declared outputs"))
    end
    return model, outputs
end

function solve(io, request, deadline)
    model, outputs = load(request["instance"])
    # The runner, not the submission, chooses and configures the solver: one
    # thread, silent, and no optimality gap, so OPTIMAL means proven.
    set_optimizer(model, HiGHS.Optimizer)
    set_silent(model)
    set_attribute(model, "threads", 1)
    set_attribute(model, "mip_rel_gap", 0.0)
    optimizing = objective_sense(model) != FEASIBILITY_SENSE

    verdict = attempt(model, deadline)
    verdict == :infeasible && return status(io, "unsat")
    verdict == :unbounded && return status(io, "error", "The objective is unbounded")
    if verdict != :solved
        return status(io, "timeout", optimizing ? "Candidate optimum was not proven" : "")
    end

    limit = request["solution_limit"]
    variables = cut_variables(outputs)
    values, current = resolved(outputs), [round(Int, JuMP.value(v)) for v in variables]
    if limit > 1
        reason = obstacle(variables)
        reason === nothing || return status(io, "unsupported", reason)
        if optimizing
            # Only assignments that reach the proven optimum may be enumerated.
            best = objective_value(model)
            objective = objective_function(model)
            @constraint(model, best - TOLERANCE <= objective <= best + TOLERANCE)
        end
    end

    seen = Set{String}()
    count = 0
    while true
        key = JSON.json(values)
        if !(key in seen)
            push!(seen, key)
            record(io, Dict("type" => "solution", "values" => values))
            count += 1
            count >= limit && return status(io, "limit")
        end
        forbid!(model, variables, current) || return status(io, "complete")
        verdict = attempt(model, deadline)
        verdict == :infeasible && return status(io, "complete")
        verdict == :solved || return status(io, "timeout")
        values, current = resolved(outputs), [round(Int, JuMP.value(v)) for v in variables]
    end
end

function main(arguments)
    record_file, deadline = arguments[1], parse(Float64, arguments[2])
    open(record_file, "w") do io
        try
            request = JSON.parsefile("/input/request.json"; dicttype = Dict{String, Any})
            solve(io, request, deadline)
        catch error
            showerror(stderr, error, catch_backtrace())
            println(stderr)
            detail = error isa LoadError ? sprint(showerror, error.error) : sprint(showerror, error)
            status(io, "error", detail)
        end
    end
end

main(ARGS)
