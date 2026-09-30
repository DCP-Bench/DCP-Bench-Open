# Crew assignment: staff each flight with flight attendants. A flight needs a
# given number of crew, of whom at least given numbers are stewards, hostesses
# and speakers of French, Spanish and German, and a person who works a flight has
# the next two flights off.
using JuMP

function build(instance)
    attributes = instance["attributes"]   # per person: steward, hostess, French, Spanish, German (0/1)
    required = instance["required_crew"]  # per flight: crew size, then the minimum per attribute
    np = length(attributes)
    nf = length(required)
    na = length(attributes[1])
    model = Model()
    @variable(model, crew[1:nf, 1:np], Bin)
    # the flight has exactly the crew size it needs
    @constraint(model, [f = 1:nf], sum(crew[f, :]) == required[f][1])
    # and at least the required number of people with each attribute
    @constraint(model, [f = 1:nf, a = 1:na],
                sum(crew[f, p] for p in 1:np if attributes[p][a] == 1) >= required[f][a + 1])
    # after a flight a person has the next two flights off
    @constraint(model, [f = 1:nf-1, p = 1:np], crew[f, p] + crew[f + 1, p] <= 1)
    @constraint(model, [f = 1:nf-2, p = 1:np], crew[f, p] + crew[f + 2, p] <= 1)
    return model, Dict("crew" => crew)
end
