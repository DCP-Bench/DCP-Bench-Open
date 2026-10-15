# Huey, Dewey and Louie: who is guilty, given that all three statements are true (the scouts cannot lie).
from paramita.modelling import Bool, If, Iff


def build(instance):
    # The problem has no instance data: the three guilt flags are the only unknowns.
    huey = Bool("huey")    # Huey is guilty
    dewey = Bool("dewey")  # Dewey is guilty
    louie = Bool("louie")  # Louie is guilty

    subject_to = []
    # Huey: Dewey and Louie have an equal share in it; if one is guilty, so is the other.
    subject_to.append(Iff(dewey, louie))
    # Dewey: If Huey is guilty, then so am I.
    subject_to.append(If(huey, dewey))
    # Louie: Dewey and I are not both guilty.
    subject_to.append(~(dewey & louie))

    outputs = {"dewey": dewey, "huey": huey, "louie": louie}
    return subject_to, outputs
