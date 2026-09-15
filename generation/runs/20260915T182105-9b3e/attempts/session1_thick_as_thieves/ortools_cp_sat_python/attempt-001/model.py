from ortools.sat.python import cp_model


def build(instance):
    """Thick as thieves: six suspects, at most two guilty, and the innocent
    tell the truth while the guilty lie.

    The puzzle states its own suspects and statements, so `instance` is unused.
    Each suspect is guilty exactly when their own statement is false, which is
    posted below as one reified claim per speaker.
    """
    del instance

    model = cp_model.CpModel()
    artie = model.new_bool_var("artie")
    bill = model.new_bool_var("bill")
    crackitt = model.new_bool_var("crackitt")
    dodgy = model.new_bool_var("dodgy")
    edgy = model.new_bool_var("edgy")
    fingers = model.new_bool_var("fingers")
    suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

    # The getaway car barely held two, so at most two of them are guilty.
    model.add(sum(suspects) <= 2)

    def conjunction(literals, name):
        """A Boolean that is true exactly when every literal holds."""
        holds = model.new_bool_var(name)
        model.add_bool_and(literals).only_enforce_if(holds)
        model.add_bool_or([~lit for lit in literals]).only_enforce_if(~holds)
        return holds

    def guilty_iff_claim_false(speaker, claim):
        model.add(speaker + claim == 1)

    # Artie: "It wasn't me."
    guilty_iff_claim_false(artie, ~artie)
    # Bill: "Crackitt was in it up to his neck."
    guilty_iff_claim_false(bill, crackitt)
    # Crackitt: "No I wasn't."
    guilty_iff_claim_false(crackitt, ~crackitt)
    # Dodgy: "If Crackitt did it, Bill did it with him." The implication holds
    # unless Crackitt is guilty and Bill is not.
    implication_fails = conjunction([crackitt, ~bill], "dodgy_claim_fails")
    guilty_iff_claim_false(dodgy, ~implication_fails)
    # Edgy: "Nobody did it alone."
    more_than_one = model.new_bool_var("more_than_one")
    model.add(sum(suspects) > 1).only_enforce_if(more_than_one)
    model.add(sum(suspects) <= 1).only_enforce_if(~more_than_one)
    guilty_iff_claim_false(edgy, more_than_one)
    # Fingers: "It was Artie and Dodgy together."
    artie_and_dodgy = conjunction([artie, dodgy], "artie_and_dodgy")
    guilty_iff_claim_false(fingers, artie_and_dodgy)

    return model, {
        "artie": artie, "bill": bill, "crackitt": crackitt,
        "dodgy": dodgy, "edgy": edgy, "fingers": fingers,
    }
