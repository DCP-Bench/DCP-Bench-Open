import z3


def build(instance):
    """Five floors: put Baker, Cooper, Fletcher, Miller and Smith on five
    different floors under the stated restrictions.
    """
    del instance

    baker, cooper, fletcher, miller, smith = people = z3.Ints("B C F M S")
    solver = z3.Solver()
    for value in people:
        solver.add(value >= 1, value <= 5)
    solver.add(z3.Distinct(people))

    solver.add(baker != 5)
    solver.add(cooper != 1)
    solver.add(z3.And(fletcher != 5, fletcher != 1))
    solver.add(miller > cooper)
    # Neither Smith nor Cooper is next door to Fletcher.
    solver.add(z3.Abs(smith - fletcher) != 1)
    solver.add(z3.Abs(fletcher - cooper) != 1)

    return solver, {
        "B": baker, "C": cooper, "F": fletcher, "M": miller, "S": smith,
    }
