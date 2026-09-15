from ortools.sat.python import cp_model


def build(instance):
    """Four islands: name, export and attraction for each of four islands laid
    out as A B over C D, with bridges A-B, C-D, A-C and B-D.

    The puzzle states its own map and clues, so `instance` is unused.  Every
    variable holds a map position: A=0, B=1, C=2, D=3.
    """
    del instance

    n = 4
    a, b, c, d = range(n)

    model = cp_model.CpModel()
    island = [model.new_int_var(0, n - 1, f"island{i}") for i in range(n)]
    pwana, quero, rayou, skern = island
    export = [model.new_int_var(0, n - 1, f"export{i}") for i in range(n)]
    alabaster, bananas, coconuts, durian_fruit = export
    attraction = [model.new_int_var(0, n - 1, f"attr{i}") for i in range(n)]
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    model.add_all_different(island)
    model.add_all_different(export)
    model.add_all_different(attraction)

    def one_of(pairs):
        """Exactly one of the listed (variable, value) pairings must hold.

        Each alternative is a conjunction, so it gets an indicator pinned in
        both directions, and at least one indicator must be true.
        """
        options = []
        for assignments in pairs:
            picked = model.new_bool_var("")
            literals = []
            for variable, value in assignments:
                matches = model.new_bool_var("")
                model.add(variable == value).only_enforce_if(matches)
                model.add(variable != value).only_enforce_if(~matches)
                literals.append(matches)
            model.add_bool_and(literals).only_enforce_if(picked)
            model.add_bool_or([lit.negated() for lit in literals]).only_enforce_if(
                ~picked
            )
            options.append(picked)
        model.add_bool_or(options)

    # 1. The koala preserve is due south of Pwana: A above C, or B above D.
    one_of([[(pwana, a), (koala_preserve, c)], [(pwana, b), (koala_preserve, d)]])
    # 2. The alabaster quarry is due west of Quero.
    one_of([[(alabaster, a), (quero, b)], [(alabaster, c), (quero, d)]])
    # 3. The resort hotel is due east of the durian fruit exporter.
    one_of(
        [[(durian_fruit, a), (resort_hotel, b)], [(durian_fruit, c), (resort_hotel, d)]]
    )
    # 4. Skern and the jai alai stadium share a north-south bridge.
    one_of([
        [(skern, a), (jai_alai_stadium, c)],
        [(skern, c), (jai_alai_stadium, a)],
        [(skern, b), (jai_alai_stadium, d)],
        [(skern, d), (jai_alai_stadium, b)],
    ])
    # 5. Rayou and the banana exporter share an east-west bridge.
    one_of([
        [(rayou, a), (bananas, b)],
        [(rayou, b), (bananas, a)],
        [(rayou, c), (bananas, d)],
        [(rayou, d), (bananas, c)],
    ])
    # 6. The ice rink and the jai alai stadium have no bridge between them, so
    #    they sit on a diagonal.
    one_of([
        [(ice_skating_rink, a), (jai_alai_stadium, d)],
        [(ice_skating_rink, d), (jai_alai_stadium, a)],
        [(ice_skating_rink, b), (jai_alai_stadium, c)],
        [(ice_skating_rink, c), (jai_alai_stadium, b)],
    ])

    return model, {
        "island": island,
        "export": export,
        "attraction": attraction,
    }
