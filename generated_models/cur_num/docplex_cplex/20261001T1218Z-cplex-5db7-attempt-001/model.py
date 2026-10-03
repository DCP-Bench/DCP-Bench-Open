"""Curious numbers (Dudeney 114): 48 plus 1 is a square, and half of 48 plus 1 is a square.
Find another number between 1 and 10000 with this property.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. Every quantity lies in 1..10000, the domain the
    # reference declares; 48 is the known example the statement excludes.
    top = 10000
    known = 48

    model = Model("cur_num")

    peculiar = model.integer_var(1, top, name="peculiar")
    half = model.integer_var(1, top, name="half")

    # A square in 1..10000 has a root in 1..100. root_is[r] is 1 when the square's root is
    # r; a square is read as sum of r * r over the chosen root, since CPLEX refuses b * b
    # for a variable b.
    roots = [r for r in range(1, top + 1) if r * r <= top]

    def square(name):
        root_is = [model.binary_var(name=f"{name}_root_{r}") for r in roots]
        model.add_constraint(model.sum(root_is) == 1)
        return model.sum(r * r * b for r, b in zip(roots, root_is))

    # 48 is already known.
    model.add(peculiar != known)
    # Adding 1 to the number gives a square.
    model.add_constraint(peculiar + 1 == square("plus_one"))
    # The number's half, plus 1, is also a square.
    model.add_constraint(peculiar == 2 * half)
    model.add_constraint(half + 1 == square("half_plus_one"))

    return model, {"peculiar": peculiar}
