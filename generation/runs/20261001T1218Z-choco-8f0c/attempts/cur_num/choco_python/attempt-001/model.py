# Curious number: 48 plus 1 is a square, and half of 48 plus 1 is a square too. Find another number
# between 1 and 10000 with this peculiarity.
from pychoco.model import Model

# The puzzle has no instance data; 48 and the range 1..10000 are its statement.
KNOWN = 48
TOP = 10000


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    def var(name):
        return model.intvar(1, TOP, name=name, bounded_domain=True)

    peculiar = var("peculiar")
    a = var("a")      # the number plus 1
    b = var("b")      # its square root
    c = var("c")      # half the number
    d = var("d")      # half the number plus 1
    e = var("e")      # its square root

    # 48 is already known, so look for another number.
    model.arithm(peculiar, "!=", KNOWN).post()
    # Adding 1 to the number gives a square.
    model.scalar([peculiar, a], [1, -1], "=", -1).post()
    model.square(a, b).post()
    # The number is even, and adding 1 to its half also gives a square.
    model.scalar([peculiar, c], [1, -2], "=", 0).post()
    model.scalar([c, d], [1, -1], "=", -1).post()
    model.square(d, e).post()

    return model, {"peculiar": peculiar}
