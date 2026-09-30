# The zebra puzzle: five houses in a row, each with a colour, a nationality, a
# pet, a drink and a job, all different, and fourteen clues. Each variable is the
# house, 0 to 4, of that colour, nationality, job, pet or drink.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    model = Model()
    groups = Dict(g => @variable(model, [1:5], lower_bound = 0, upper_bound = 4, integer = true)
                  for g in ("colors", "nations", "jobs", "pets", "drinks"))
    for x in values(groups)
        @constraint(model, x in MOI.AllDifferent(5))
    end
    yellow, green, red, white, blue = groups["colors"]
    italy, spain, japan, england, norway = groups["nations"]
    painter, sculptor, diplomat, pianist, doctor = groups["jobs"]
    cat, zebra, bear, snails, horse = groups["pets"]
    milk, water, tea, coffee, juice = groups["drinks"]
    @constraint(model, painter == horse)        # the painter owns the horse
    @constraint(model, diplomat == coffee)      # the diplomat drinks coffee
    @constraint(model, white == milk)           # milk is drunk in the white house
    @constraint(model, spain == painter)        # the Spaniard is a painter
    @constraint(model, england == red)          # the Englishman lives in the red house
    @constraint(model, snails == sculptor)      # the sculptor owns the snails
    @constraint(model, green + 1 == red)        # green is just left of red
    @constraint(model, blue + 1 == norway)      # the Norwegian is just right of blue
    @constraint(model, doctor == milk)          # the doctor drinks milk
    @constraint(model, japan == diplomat)       # the diplomat is Japanese
    @constraint(model, norway == zebra)         # the Norwegian owns the zebra
    # green is next to white, and the horse's owner next to the diplomat: each
    # difference is 2 * side - 1, that is -1 or 1
    @variable(model, side[1:2], Bin)
    @constraint(model, green - white == 2 * side[1] - 1)
    @constraint(model, horse - diplomat == 2 * side[2] - 1)
    # the Italian lives in the red, the white or the green house
    @variable(model, house[1:3], Bin)
    @constraint(model, sum(house) >= 1)
    @constraint(model, house[1] --> {italy == red})
    @constraint(model, house[2] --> {italy == white})
    @constraint(model, house[3] --> {italy == green})
    return model, Dict(g => x for (g, x) in groups)
end
