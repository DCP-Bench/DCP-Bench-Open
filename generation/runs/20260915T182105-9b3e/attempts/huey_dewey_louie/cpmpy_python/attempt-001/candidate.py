import cpmpy as cp


def build(instance):
    """Huey, Dewey and Louie: three cub scouts who cannot lie, so each of their
    statements is simply true.

    The puzzle states its own three claims, so `instance` is unused.
    """
    del instance

    p = cp.boolvar(shape=3, name="p")
    huey, dewey, louie = p

    model = cp.Model(
        # Huey: Dewey and Louie share equally, so one is guilty exactly when
        # the other is.
        dewey == louie,
        # Dewey: if Huey is guilty, so am I.
        huey.implies(dewey),
        # Louie: Dewey and I are not both guilty.
        ~(dewey & louie),
    )

    return model, {"huey": huey, "dewey": dewey, "louie": louie}
