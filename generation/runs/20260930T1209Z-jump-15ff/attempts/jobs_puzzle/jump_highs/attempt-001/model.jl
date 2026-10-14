# Jobs puzzle: four people hold eight different jobs, two each, subject to clues
# about who is not what.
using JuMP

const JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    model = Model()
    # holds[j, p] = 1 when person p - 1 holds job j
    @variable(model, holds[1:8, 1:4], Bin)
    @constraint(model, [j = 1:8], sum(holds[j, :]) == 1)
    @constraint(model, [p = 1:4], sum(holds[:, p]) == 2)   # two jobs each
    job(name) = findfirst(==(name), JOBS)
    apart(a, b) = @constraint(model, [p = 1:4], holds[job(a), p] + holds[job(b), p] <= 1)
    not_held_by(a, person) = fix(holds[job(a), person + 1], 0; force = true)
    # 1. the nurse is not the teacher, the police officer or the clerk
    apart("nurse", "teacher"); apart("nurse", "police_officer"); apart("nurse", "clerk")
    # 2. the clerk is not the chef
    apart("clerk", "chef")
    # 3. person 0 is not the boxer
    not_held_by("boxer", 0)
    # 4. person 3 is not the teacher, the police officer or the nurse
    not_held_by("teacher", 3); not_held_by("police_officer", 3); not_held_by("nurse", 3)
    # 5. person 0, the chef and the police officer went golfing, so they are three people
    not_held_by("chef", 0); not_held_by("police_officer", 0); apart("chef", "police_officer")
    @variable(model, 0 <= person[1:8] <= 3, Int)
    @constraint(model, [j = 1:8], person[j] == sum((p - 1) * holds[j, p] for p in 1:4))
    return model, Dict(JOBS[j] => person[j] for j in 1:8)
end
