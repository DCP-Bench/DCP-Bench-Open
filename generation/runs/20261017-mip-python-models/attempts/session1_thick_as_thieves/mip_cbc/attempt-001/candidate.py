# Thick as thieves: six suspects (artie, bill, crackitt, dodgy, edgy, fingers).
# Each output is 1 if the suspect is guilty, 0 if innocent.
# Innocent suspects tell the truth, guilty suspects lie. Only two can fit in the car.
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    a = model.add_var("artie", var_type=mip.BINARY)
    b = model.add_var("bill", var_type=mip.BINARY)
    c = model.add_var("crackitt", var_type=mip.BINARY)
    d = model.add_var("dodgy", var_type=mip.BINARY)
    e = model.add_var("edgy", var_type=mip.BINARY)
    f = model.add_var("fingers", var_type=mip.BINARY)

    # The getaway car was barely big enough to hold two, so at most two are guilty
    # (the inspector reckons at least four are innocent). Count the guilty with one-hot
    # binaries t0, t1, t2 for zero, one or two guilty suspects.
    t0 = model.add_var("count_zero", var_type=mip.BINARY)
    t1 = model.add_var("count_one", var_type=mip.BINARY)
    t2 = model.add_var("count_two", var_type=mip.BINARY)
    model.add_constr(t0 + t1 + t2 == 1)
    model.add_constr(mip.xsum([a, b, c, d, e, f]) == t1 + 2 * t2)

    # Artie: "It wasn't me." The statement is "I am innocent", so the guilty-or-not
    # status is the same as the statement's truth value. Nothing to encode.

    # Bill: "Crackitt was in it up to his neck." Bill is innocent exactly when
    # the statement "Crackitt is guilty" is true, so Bill is guilty exactly when Crackitt is innocent.
    model.add_constr(b + c == 1)

    # Crackitt: "No I wasn't." Same reasoning as Artie: the statement is the negation of
    # Crackitt's own guilt, so it is consistent with any value. Nothing to encode.

    # Dodgy: "If Crackitt did it, Bill did it with him." The statement is (c implies b).
    # Dodgy is guilty exactly when the statement is false, that is when c = 1 and b = 0.
    model.add_constr(d >= c - b)
    model.add_constr(d <= c)
    model.add_constr(d + b <= 1)

    # Edgy: "Nobody did it alone." The statement is "the number of guilty is not one".
    # Edgy is guilty exactly when the statement is false, that is when exactly one is guilty.
    model.add_constr(e == t1)

    # Fingers: "That's right: it was Artie and Dodgy together." The statement is (a and d).
    # Let w = a and d (binary), then Fingers is guilty exactly when the statement is false.
    w = model.add_var("artie_and_dodgy", var_type=mip.BINARY)
    model.add_constr(w <= a)
    model.add_constr(w <= d)
    model.add_constr(w >= a + d - 1)
    model.add_constr(f + w == 1)

    return model, {
        "artie": a,
        "bill": b,
        "crackitt": c,
        "dodgy": d,
        "edgy": e,
        "fingers": f,
    }
