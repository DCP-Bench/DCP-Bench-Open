from pychoco.model import Model


def build(instance):
    """Huey, Dewey and Louie: three cub scouts who cannot lie, so each of their
    statements is simply true.
    """
    del instance

    model = Model()
    huey = model.boolvar(name="huey")
    dewey = model.boolvar(name="dewey")
    louie = model.boolvar(name="louie")

    # Huey: Dewey and Louie share equally.
    model.arithm(dewey, "=", louie).post()
    # Dewey: if Huey is guilty, so am I.
    model.arithm(huey, "<=", dewey).post()
    # Louie: Dewey and I are not both guilty.
    model.scalar([dewey, louie], [1, 1], "<=", 1).post()

    return model, {"huey": huey, "dewey": dewey, "louie": louie}
