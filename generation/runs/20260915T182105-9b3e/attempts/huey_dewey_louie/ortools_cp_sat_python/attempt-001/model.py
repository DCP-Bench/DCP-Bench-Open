from ortools.sat.python import cp_model


def build(instance):
    """Huey, Dewey and Louie: three cub scouts who cannot lie, so each of their
    statements is simply true.

    The puzzle states its own three claims, so `instance` is unused.
    """
    del instance

    model = cp_model.CpModel()
    huey = model.new_bool_var("huey")
    dewey = model.new_bool_var("dewey")
    louie = model.new_bool_var("louie")

    # Huey: Dewey and Louie share equally, so one is guilty exactly when the
    # other is.
    model.add(dewey == louie)
    # Dewey: if Huey is guilty, so am I.
    model.add_implication(huey, dewey)
    # Louie: Dewey and I are not both guilty.
    model.add_bool_or([~dewey, ~louie])

    return model, {"huey": huey, "dewey": dewey, "louie": louie}
