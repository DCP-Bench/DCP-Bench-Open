# Thick as thieves: six suspects, at most two of them guilty; the innocent tell the truth and the
# guilty lie. From their statements, who is guilty?
from pychoco.model import Model

# The puzzle has no instance data; the suspects and their statements are its statement.
MAX_GUILTY = 2  # the getaway car held at most two


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    names = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]
    guilty = {name: model.boolvar(name=name) for name in names}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[name] for name in names)

    # At most two are guilty, because the getaway car was small.
    n_guilty = model.intvar(0, MAX_GUILTY, name="n_guilty")
    model.sum(list(guilty.values()), "=", n_guilty).post()

    # A suspect is guilty exactly when their statement is false.
    # Artie: "It wasn't me." and Crackitt: "No I wasn't." are false exactly when the speaker is
    # guilty, so they hold for either value and add no constraint.
    # Bill: "Crackitt was in it up to his neck." Bill is guilty exactly when Crackitt is innocent.
    model.arithm(bill, "+", crackitt, "=", 1).post()
    # Dodgy: "If Crackitt did it, Bill did it with him." False exactly when Crackitt is guilty and
    # Bill is not: dodgy = crackitt and not bill.
    model.arithm(dodgy, "<=", crackitt).post()
    model.arithm(dodgy, "+", bill, "<=", 1).post()
    model.scalar([dodgy, crackitt, bill], [1, -1, 1], ">=", 0).post()
    # Edgy: "Nobody did it alone." (more than one is guilty). False exactly when at most one is.
    model.arithm(n_guilty, "<=", 1).reify_with(edgy)
    # Fingers: "It was Artie and Dodgy together." False exactly when not both are guilty:
    # fingers = not (artie and dodgy).
    model.arithm(fingers, "+", artie, ">=", 1).post()
    model.arithm(fingers, "+", dodgy, ">=", 1).post()
    model.sum([fingers, artie, dodgy], "<=", 2).post()

    return model, guilty
