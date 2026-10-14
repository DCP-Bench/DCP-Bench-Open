# Arch friends: Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats, purple
# pumps, suede sandals) at four different stores (Foot Farm, Heels in a Handcart, The Shoe
# Palace, Tootsies), one per stop. Find the stop (1..4) at which she bought each pair and
# the stop at which she visited each store.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 4   # number of shoe pairs, of stores, and of stops

    model = Model()

    # shoes[k] = the stop at which pair k was bought, store[k] = the stop at which store k was
    # visited; both are bounded to the stops 1..n
    @variable(model, 1 <= shoes[1:n] <= n, Int)
    @variable(model, 1 <= store[1:n] <= n, Int)
    ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = shoes
    footfarm, heelsinahandcart, theshoepalace, tootsies = store

    # each stop buys one pair and visits one store
    @constraint(model, shoes in MOI.AllDifferent(n))
    @constraint(model, store in MOI.AllDifferent(n))

    # 1. Harriet bought the fuchsia flats at Heels in a Handcart
    @constraint(model, fuchsiaflats == heelsinahandcart)

    # 2. The store she visited just after buying her purple pumps was not Tootsies:
    #    purplepumps + 1 != tootsies. A binary picks which side of the difference holds
    #    (the two differences lie in -2..4 and -4..2, which gives the big-M values 3 and 5).
    side = @variable(model, binary = true)
    @constraint(model, purplepumps + 1 - tootsies >= 1 - 3 * side)
    @constraint(model, tootsies - purplepumps - 1 >= 1 - 5 * (1 - side))

    # 3. The Foot Farm was Harriet's second stop
    @constraint(model, footfarm == 2)

    # 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals
    @constraint(model, theshoepalace + 2 == suedesandals)

    return model, Dict("ecruespadrilles" => ecruespadrilles, "fuchsiaflats" => fuchsiaflats,
                       "purplepumps" => purplepumps, "suedesandals" => suedesandals,
                       "footfarm" => footfarm, "heelsinahandcart" => heelsinahandcart,
                       "theshoepalace" => theshoepalace, "tootsies" => tootsies)
end
