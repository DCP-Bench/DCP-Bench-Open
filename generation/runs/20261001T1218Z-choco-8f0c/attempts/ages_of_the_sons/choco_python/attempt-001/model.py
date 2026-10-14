# Ages of the sons: the product of the three sons' ages is 36, their sum alone does not decide
# them, and there is a single oldest son. Find the ages, oldest first.
from pychoco.model import Model

# The puzzle has no instance data: the product 36 is part of its statement, and it bounds every
# age by 36.
PRODUCT = 36


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # A1 >= A2 >= A3 are the sons' ages, oldest first
    a = [model.intvar(0, PRODUCT, name=f"A{i + 1}") for i in range(3)]
    # B1 >= B2 >= B3 is another triple of ages the mathematician cannot rule out from the sum
    b = [model.intvar(0, PRODUCT, name=f"B{i + 1}") for i in range(3)]

    # There is an oldest son (no twin of the oldest): A1 > A2 >= A3.
    model.arithm(a[0], ">", a[1]).post()
    model.arithm(a[1], ">=", a[2]).post()
    # The other triple is listed oldest first too.
    model.arithm(b[0], ">=", b[1]).post()
    model.arithm(b[1], ">=", b[2]).post()

    # The product of the ages is 36, for both triples.
    product = model.intvar(PRODUCT, PRODUCT, name="product")
    for ages, tag in ((a, "A"), (b, "B")):
        pair = model.intvar(0, PRODUCT, name=f"{tag}12")
        model.times(ages[0], ages[1], pair).post()
        model.times(pair, ages[2], product).post()

    # The number of windows (the sum of the ages) does not decide the triple: another triple with
    # the same sum exists, and it differs in its oldest age.
    model.scalar(a + b, [1, 1, 1, -1, -1, -1], "=", 0).post()
    model.arithm(a[0], "!=", b[0]).post()

    return model, {"A1": a[0], "A2": a[1], "A3": a[2]}
