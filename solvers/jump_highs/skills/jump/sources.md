# Sources for `jump`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://jump.dev/JuMP.jl/stable/> — JuMP 1.32.0 manual: variables, constraints, containers, indicator constraints, objectives and solution queries, accessed 2026-09-30
- <https://jump.dev/MathOptInterface.jl/stable/reference/standard_form/> — the MOI sets used here (AllDifferent, Table, Circuit, CountDistinct, CountBelongs, SOS1) and the bridges that reformulate them into MILP
- <https://ergo-code.github.io/HiGHS/stable/> — HiGHS options, including `mip_rel_gap` and `threads`
- <https://hub.docker.com/_/julia> — `julia:1.12-bookworm`, Julia 1.12.7, the base image
- `solvers/jump_highs/Manifest.toml` — the exact package versions: JuMP 1.32.0, HiGHS.jl 1.26.0, HiGHS_jll 1.15.1, JSON 1.10.0

Every claim about what works was checked by running Julia inside the
`dcp-eval/jump_highs:v1` image with HiGHS attached:

- `MOI.AllDifferent`, `MOI.Table` (with a `Float64` tuple matrix), `MOI.Circuit`,
  `MOI.CountDistinct`, `MOI.CountBelongs`, `SOS1`, and indicator constraints
  `b --> {...}` and `!b --> {...}` solve to OPTIMAL with the expected values.
- `MOI.AllDifferent` over unbounded integers stops with
  `BridgeRequiresFiniteDomainError`; `MOI.Table` with an integer matrix,
  `MOI.Reified` and a product of two binaries in a constraint are rejected as
  unsupported constraints; `@constraint(model, x != y)` fails when the macro
  expands, naming the line.
- `JSON.parsefile(...; dicttype = Dict{String, Any})`, as the driver reads the
  request, gives `Dict{String, Any}`, `Vector{Any}` arrays, `String`, `Bool` and
  nested `Dict`; `permutedims(reduce(hcat, rows))` makes a `Matrix` from a list
  of rows.
- Outputs: a `Bin` matrix comes back as its rows, a container over `0:2` as a
  list, `sum(m)` as an integer, and a string and a `Bool` unchanged.
- Loop scoping, the error on re-registering a named variable, anonymous
  variables and `@expression` behave as the traps say.
