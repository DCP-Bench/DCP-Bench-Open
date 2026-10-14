# Allergy: four friends (Debra, Janet, Hugh, Rick) are each allergic to something different
# (eggs, mold, nuts, ragweed) and each has a different surname (Baxter, Lemon, Malone,
# Fleet). Match every allergy and every surname to a friend from the clues.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 4
    # friends are numbered Debra = 0, Janet = 1, Hugh = 2, Rick = 3 (as the problem prints them)
    debra, janet, hugh, rick = 0, 1, 2, 3
    # positions of the allergies and of the surnames, in the order the problem lists them
    eggs_i, mold_i, nuts_i, ragweed_i = 1, 2, 3, 4
    baxter_i, lemon_i, malone_i, fleet_i = 1, 2, 3, 4

    model = Model()

    # has_food[f, i] = 1 when friend i - 1 is allergic to food f, has_name[s, i] = 1 when
    # friend i - 1 has surname s. Each food and each surname belongs to exactly one friend and
    # each friend has exactly one food and one surname (all different).
    @variable(model, has_food[1:n, 1:n], Bin)
    @variable(model, has_name[1:n, 1:n], Bin)
    @constraint(model, [f = 1:n], sum(has_food[f, :]) == 1)
    @constraint(model, [i = 1:n], sum(has_food[:, i]) == 1)
    @constraint(model, [s = 1:n], sum(has_name[s, :]) == 1)
    @constraint(model, [i = 1:n], sum(has_name[:, i]) == 1)

    # food_of[f] and name_of[s] = the friend (0..3) allergic to food f or with surname s. These
    # are the declared outputs, kept as bounded integer variables tied to the indicators.
    @variable(model, 0 <= food_of[1:n] <= n - 1, Int)
    @variable(model, 0 <= name_of[1:n] <= n - 1, Int)
    @constraint(model, [f = 1:n], food_of[f] == sum((i - 1) * has_food[f, i] for i in 1:n))
    @constraint(model, [s = 1:n], name_of[s] == sum((i - 1) * has_name[s, i] for i in 1:n))

    # Rick is not allergic to mold
    @constraint(model, has_food[mold_i, rick+1] == 0)
    # Baxter is allergic to eggs: the same friend has both
    @constraint(model, food_of[eggs_i] == name_of[baxter_i])
    # Hugh is neither surnamed Lemon nor Fleet
    @constraint(model, has_name[lemon_i, hugh+1] == 0)
    @constraint(model, has_name[fleet_i, hugh+1] == 0)
    # Debra is allergic to ragweed
    @constraint(model, food_of[ragweed_i] == debra)
    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold
    @constraint(model, has_name[lemon_i, janet+1] == 0)
    @constraint(model, has_food[eggs_i, janet+1] == 0)
    @constraint(model, has_food[mold_i, janet+1] == 0)

    return model, Dict("eggs" => food_of[eggs_i], "mold" => food_of[mold_i],
                       "nuts" => food_of[nuts_i], "ragweed" => food_of[ragweed_i],
                       "baxter" => name_of[baxter_i], "lemon" => name_of[lemon_i],
                       "malone" => name_of[malone_i], "fleet" => name_of[fleet_i])
end
