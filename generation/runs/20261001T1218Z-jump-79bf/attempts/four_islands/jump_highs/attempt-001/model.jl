# Four islands: four islands (Pwana, Quero, Rayou, Skern) each have a different export
# (alabaster, bananas, coconuts, durian fruit) and a different attraction (resort hotel, ice
# skating rink, jai alai stadium, koala preserve). They sit on a map of four places
#   A B
#   C D
# joined by bridges A-B, A-C, B-D, C-D. Find the map position (A = 0, B = 1, C = 2, D = 3)
# of every island, export and attraction from six clues.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 4
    A, B, C, D = 0, 1, 2, 3   # map positions: A top left, B top right, C bottom left, D bottom right

    model = Model()

    # island[k], export_at[k], attraction[k] = the map position of the k-th island, export and
    # attraction, in the order the problem lists them
    @variable(model, 0 <= island[1:n] <= n - 1, Int)
    @variable(model, 0 <= export_at[1:n] <= n - 1, Int)
    @variable(model, 0 <= attraction[1:n] <= n - 1, Int)
    pwana, quero, rayou, skern = island
    alabaster, bananas, coconuts, durian_fruit = export_at
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    # every island, export and attraction sits at a different position
    @constraint(model, island in MOI.AllDifferent(n))
    @constraint(model, export_at in MOI.AllDifferent(n))
    @constraint(model, attraction in MOI.AllDifferent(n))

    # one_of(cases): at least one case holds, where a case is a list of (variable, position)
    # pairs that must all hold. Each case gets a binary; when it is 1 every variable of the case
    # equals its position (the difference is at most n - 1, so n - 1 is the big-M), and at
    # least one binary must be 1.
    function one_of(cases)
        chosen = @variable(model, [1:length(cases)], Bin)
        for (c, case) in enumerate(cases), (x, position) in case
            @constraint(model, x - position <= (n - 1) * (1 - chosen[c]))
            @constraint(model, position - x <= (n - 1) * (1 - chosen[c]))
        end
        @constraint(model, sum(chosen) >= 1)
    end

    # 1. The island with the koala preserve is due south of Pwana
    one_of([((pwana, A), (koala_preserve, C)), ((pwana, B), (koala_preserve, D))])
    # 2. The island with the largest alabaster quarry is due west of Quero
    one_of([((alabaster, A), (quero, B)), ((alabaster, C), (quero, D))])
    # 3. The island with the resort hotel is due east of the one that exports durian fruit
    one_of([((durian_fruit, A), (resort_hotel, B)), ((durian_fruit, C), (resort_hotel, D))])
    # 4. Skern and the island with the jai alai stadium are connected by a north-south bridge
    one_of([((skern, A), (jai_alai_stadium, C)), ((skern, C), (jai_alai_stadium, A)),
            ((skern, B), (jai_alai_stadium, D)), ((skern, D), (jai_alai_stadium, B))])
    # 5. Rayou and the island that exports bananas are connected by an east-west bridge
    one_of([((rayou, A), (bananas, B)), ((rayou, B), (bananas, A)),
            ((rayou, C), (bananas, D)), ((rayou, D), (bananas, C))])
    # 6. The islands with the ice skating rink and the jai alai stadium are not connected by a
    #    bridge, so they are diagonal to each other
    one_of([((ice_skating_rink, A), (jai_alai_stadium, D)), ((ice_skating_rink, D), (jai_alai_stadium, A)),
            ((ice_skating_rink, B), (jai_alai_stadium, C)), ((ice_skating_rink, C), (jai_alai_stadium, B))])

    return model, Dict("island" => island, "export" => export_at, "attraction" => attraction)
end
