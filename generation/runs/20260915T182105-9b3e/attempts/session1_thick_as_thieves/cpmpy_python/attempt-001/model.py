import cpmpy as cp


def build(instance):
    """Thick as thieves: six suspects, at most two guilty, and the innocent
    tell the truth while the guilty lie.

    The puzzle states its own suspects and statements, so `instance` is unused.
    """
    del instance

    artie = cp.boolvar(name="Artie")
    bill = cp.boolvar(name="Bill")
    crackitt = cp.boolvar(name="Crackitt")
    dodgy = cp.boolvar(name="Dodgy")
    edgy = cp.boolvar(name="Edgy")
    fingers = cp.boolvar(name="Fingers")
    suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

    model = cp.Model()
    # The getaway car barely held two, so at most two of them are guilty.
    model += cp.sum(suspects) <= 2

    # Each suspect is guilty exactly when their own statement is false.
    claims = [
        (artie, ~artie),                  # "It wasn't me."
        (bill, crackitt),                 # "Crackitt was in it."
        (crackitt, ~crackitt),            # "No I wasn't."
        (dodgy, crackitt.implies(bill)),  # "If Crackitt did it, so did Bill."
        (edgy, cp.sum(suspects) > 1),     # "Nobody did it alone."
        (fingers, artie & dodgy),         # "It was Artie and Dodgy."
    ]
    for speaker, claim in claims:
        model += speaker == ~claim

    return model, {
        "artie": artie, "bill": bill, "crackitt": crackitt,
        "dodgy": dodgy, "edgy": edgy, "fingers": fingers,
    }
