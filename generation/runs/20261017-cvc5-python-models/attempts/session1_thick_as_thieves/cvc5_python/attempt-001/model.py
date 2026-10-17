# Problem: session1_thick_as_thieves. Six suspects (artie, bill, crackitt, dodgy,
# edgy, fingers) after a robbery. Each is guilty or innocent. Innocent suspects tell
# the truth and guilty suspects lie. Output: whether each suspect is guilty.
import cvc5.pythonic as cz
from cvc5.pythonic import And, Implies, Not


def build(instance):
    artie, bill, crackitt, dodgy, edgy, fingers = cz.Bools(
        "artie bill crackitt dodgy edgy fingers"
    )
    guilty = [artie, bill, crackitt, dodgy, edgy, fingers]
    count = cz.Sum([cz.If(g, 1, 0) for g in guilty])

    constraints = [
        # The getaway car was barely big enough to hold two, and at least four of them
        # were innocent, so at most two are guilty. The guilty one or ones means at
        # least one is guilty.
        count <= 2,
        count >= 1,
        # ARTIE: "It wasn't me." Its truth value is exactly that of innocence, so it
        # imposes no constraint on the guilt values.
        # BILL: "Crackitt was in it up to his neck." Bill tells the truth exactly when
        # he is innocent.
        crackitt == Not(bill),
        # CRACKITT: "No I wasn't." Its truth value is exactly that of innocence, so it
        # imposes no constraint on the guilt values.
        # DODGY: "If Crackitt did it, Bill did it with him." Dodgy tells the truth
        # exactly when he is innocent.
        Implies(crackitt, bill) == Not(dodgy),
        # EDGY: "Nobody did it alone." Edgy tells the truth exactly when he is innocent.
        (count != 1) == Not(edgy),
        # FINGERS: "That's right: it was Artie and Dodgy together." Fingers tells the
        # truth exactly when he is innocent.
        And(artie, dodgy) == Not(fingers),
    ]
    outputs = {
        "artie": artie,
        "bill": bill,
        "crackitt": crackitt,
        "dodgy": dodgy,
        "edgy": edgy,
        "fingers": fingers,
    }
    return constraints, outputs
