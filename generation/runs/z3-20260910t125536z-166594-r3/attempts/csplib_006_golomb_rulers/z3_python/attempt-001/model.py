import z3


def build(instance):
    size = instance["size"]
    marks = [z3.Int(f"marks_{i}") for i in range(size)]
    constraints = [z3.And(mark >= 0, mark <= size * size) for mark in marks]
    constraints.append(marks[0] == 0)
    for i in range(size - 1):
        constraints.append(marks[i] < marks[i + 1])
    # Every pairwise distance along the ruler is distinct.
    distances = [marks[j] - marks[i] for i in range(size - 1) for j in range(i + 1, size)]
    constraints.append(z3.Distinct(distances))
    length = marks[size - 1]
    return constraints, {"marks": marks, "length": length}, ("minimize", length)
