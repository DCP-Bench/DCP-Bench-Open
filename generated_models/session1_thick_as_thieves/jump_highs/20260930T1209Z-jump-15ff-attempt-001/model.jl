# Thick as thieves: six suspects, at most two of them guilty. The innocent tell
# the truth and the guilty lie in what they said.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    model = Model()
    @variable(model, g[1:6], Bin)    # 1 when guilty
    artie, bill, crackitt, dodgy, edgy, fingers = g
    # the getaway car held two, so at most two are guilty
    @constraint(model, sum(g) <= 2)
    # A suspect is guilty exactly when what he said is false.
    # Artie ("It wasn't me") and Crackitt ("No I wasn't") each say something false
    # exactly when guilty, whatever the case, so they restrict nothing.
    # Bill: "Crackitt was in it up to his neck." Guilty exactly when Crackitt is not.
    @constraint(model, bill + crackitt == 1)
    # Dodgy: "If Crackitt did it, Bill did it with him." False exactly when Crackitt
    # is guilty and Bill is not: dodgy = crackitt and not bill.
    @constraint(model, dodgy <= crackitt)
    @constraint(model, dodgy <= 1 - bill)
    @constraint(model, dodgy >= crackitt - bill)
    # Edgy: "Nobody did it alone." False exactly when at most one is guilty.
    @constraint(model, sum(g) >= 2 - 2 * edgy)          # edgy innocent: two or more guilty
    @constraint(model, sum(g) <= 1 + 5 * (1 - edgy))    # edgy guilty: at most one
    # Fingers: "It was Artie and Dodgy together." Fingers = not (artie and dodgy).
    @constraint(model, fingers >= 1 - artie)
    @constraint(model, fingers >= 1 - dodgy)
    @constraint(model, fingers <= 2 - artie - dodgy)
    return model, Dict("artie" => artie, "bill" => bill, "crackitt" => crackitt,
                       "dodgy" => dodgy, "edgy" => edgy, "fingers" => fingers)
end
