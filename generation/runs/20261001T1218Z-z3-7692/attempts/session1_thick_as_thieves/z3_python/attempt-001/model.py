# Thick as thieves: six suspects questioned after a robbery; the innocent tell the
# truth, the guilty lie, and at most two were in the (two-seat) getaway car.
# Decide who is guilty.
import z3


def build(instance):
    del instance  # the puzzle states its own suspects and statements

    # True when the suspect is guilty.
    artie, bill, crackitt, dodgy, edgy, fingers = suspects = z3.Bools(
        "artie bill crackitt dodgy edgy fingers")

    solver = z3.Solver()

    # The getaway car held at most two, so at most two suspects are guilty.
    solver.add(z3.AtMost(*suspects, 2))

    # Each guilty suspect lies and each innocent one tells the truth: a suspect
    # is guilty exactly when what he said is false.

    # ARTIE: "It wasn't me."
    solver.add(artie == z3.Not(z3.Not(artie)))

    # BILL: "Crackitt was in it up to his neck."
    solver.add(bill == z3.Not(crackitt))

    # CRACKITT: "No I wasn't."
    solver.add(crackitt == z3.Not(z3.Not(crackitt)))

    # DODGY: "If Crackitt did it, Bill did it with him."
    solver.add(dodgy == z3.Not(z3.Implies(crackitt, bill)))

    # EDGY: "Nobody did it alone." (at least two are guilty)
    solver.add(edgy == z3.Not(z3.AtLeast(*suspects, 2)))

    # FINGERS: "That's right: it was Artie and Dodgy together."
    solver.add(fingers == z3.Not(z3.And(artie, dodgy)))

    return solver, {"artie": artie, "bill": bill, "crackitt": crackitt,
                    "dodgy": dodgy, "edgy": edgy, "fingers": fingers}
