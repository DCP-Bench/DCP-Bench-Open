import cpmpy as cp


def build(instance):
    """Four islands: name, export and attraction for each of four islands laid
    out as A B over C D, with bridges A-B, C-D, A-C and B-D.

    The puzzle states its own map and clues, so `instance` is unused.  Every
    variable holds a map position: A=0, B=1, C=2, D=3.
    """
    del instance

    n = 4
    a, b, c, d = range(n)

    island = cp.intvar(0, n - 1, shape=n, name="island")
    pwana, quero, rayou, skern = island
    export = cp.intvar(0, n - 1, shape=n, name="export")
    alabaster, bananas, coconuts, durian_fruit = export
    attraction = cp.intvar(0, n - 1, shape=n, name="attraction")
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    model = cp.Model(
        cp.AllDifferent(island),
        cp.AllDifferent(export),
        cp.AllDifferent(attraction),
    )

    # 1. The koala preserve is due south of Pwana: A above C, or B above D.
    model += ((pwana == a) & (koala_preserve == c)) | (
        (pwana == b) & (koala_preserve == d)
    )
    # 2. The alabaster quarry is due west of Quero.
    model += ((alabaster == a) & (quero == b)) | (
        (alabaster == c) & (quero == d)
    )
    # 3. The resort hotel is due east of the durian fruit exporter.
    model += ((durian_fruit == a) & (resort_hotel == b)) | (
        (durian_fruit == c) & (resort_hotel == d)
    )
    # 4. Skern and the jai alai stadium share a north-south bridge.
    model += (
        ((skern == a) & (jai_alai_stadium == c))
        | ((skern == c) & (jai_alai_stadium == a))
        | ((skern == b) & (jai_alai_stadium == d))
        | ((skern == d) & (jai_alai_stadium == b))
    )
    # 5. Rayou and the banana exporter share an east-west bridge.
    model += (
        ((rayou == a) & (bananas == b))
        | ((rayou == b) & (bananas == a))
        | ((rayou == c) & (bananas == d))
        | ((rayou == d) & (bananas == c))
    )
    # 6. The ice rink and the jai alai stadium have no bridge between them, so
    #    they sit on a diagonal.
    model += (
        ((ice_skating_rink == a) & (jai_alai_stadium == d))
        | ((ice_skating_rink == d) & (jai_alai_stadium == a))
        | ((ice_skating_rink == b) & (jai_alai_stadium == c))
        | ((ice_skating_rink == c) & (jai_alai_stadium == b))
    )

    return model, {
        "island": island,
        "export": export,
        "attraction": attraction,
    }
