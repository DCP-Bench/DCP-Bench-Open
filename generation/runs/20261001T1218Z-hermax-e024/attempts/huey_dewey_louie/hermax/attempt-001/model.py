# Huey, Dewey and Louie: three cub scouts, who cannot lie, make statements about who is
# guilty. Decide who (if any) is guilty.
from hermax.model import Model


def build(instance):
    # The statements are fixed by the problem; the instance carries no data.
    m = Model()
    huey = m.bool("huey")    # Huey is guilty
    dewey = m.bool("dewey")  # Dewey is guilty
    louie = m.bool("louie")  # Louie is guilty

    # Huey: Dewey and Louie have an equal share in it; if one is guilty, so is the other.
    m &= (~dewey | louie)
    m &= (dewey | ~louie)
    # Dewey: if Huey is guilty, then so am I.
    m &= (~huey | dewey)
    # Louie: Dewey and I are not both guilty.
    m &= (~dewey | ~louie)

    return m, {"huey": huey, "dewey": dewey, "louie": louie}
