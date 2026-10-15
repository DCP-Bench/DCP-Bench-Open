# Inspector Korner's puzzle: six suspects, who is guilty?
# Each suspect is one Boolean: true when that suspect took part in the robbery.
from paramita.modelling import Bool, If, Iff, Or

SUSPECTS = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]


def build(instance):
    # The problem gives no instance fields; the suspects and their statements come from the problem statement.
    guilty = {s: Bool(f"guilty_{s}") for s in SUSPECTS}
    guilty_count = sum(guilty.values())

    cons = []

    # The getaway car was barely big enough to hold two, so at most two are guilty.
    # Inspector Korner reckoned at least four were innocent, which gives the same bound.
    cons.append(guilty_count <= 2)
    # "the guilty one or ones": at least one suspect is guilty.
    cons.append(guilty_count >= 1)

    # Innocent suspects tell the truth and guilty suspects lie.
    # So each statement is true exactly when its speaker is innocent.

    # ARTIE: "It wasn't me."
    cons.append(Iff(~guilty["artie"], ~guilty["artie"]))
    # BILL: "Crackitt was in it up to his neck."
    cons.append(Iff(~guilty["bill"], guilty["crackitt"]))
    # CRACKITT: "No I wasn't."
    cons.append(Iff(~guilty["crackitt"], ~guilty["crackitt"]))
    # DODGY: "If Crackitt did it, Bill did it with him."
    cons.append(Iff(~guilty["dodgy"], If(guilty["crackitt"], guilty["bill"])))
    # EDGY: "Nobody did it alone." (the guilty group is not exactly one person)
    cons.append(Iff(~guilty["edgy"], Or(guilty_count >= 2, guilty_count == 0)))
    # FINGERS: "That's right: it was Artie and Dodgy together." (exactly those two are guilty)
    cons.append(Iff(~guilty["fingers"], guilty["artie"] & guilty["dodgy"] & (guilty_count == 2)))

    outputs = {s: guilty[s] for s in SUSPECTS}
    return cons, outputs
