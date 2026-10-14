# Quasigroup existence, QG3.m: fill an m x m table with the numbers 0..m-1 so that every number
# occurs once in each row and each column (a Latin square) and (a*b)*(b*a) = a for all a, b,
# where a*b is the table entry in row a, column b.
from exact import Exact


def build(instance):
    m = instance["m"]  # order of the quasigroup

    solver = Exact()

    # quasigroup[i][j] = the entry a*b for a = i, b = j, a value in 0..m-1
    quasigroup = [[f"q_{i}_{j}" for j in range(m)] for i in range(m)]
    for i in range(m):
        for j in range(m):
            solver.addVariable(quasigroup[i][j], 0, m - 1)

    # Entries are used as table indices in the QG3 property, which Exact cannot express on
    # integer variables. So each cell also gets one 0/1 variable per value:
    # is_value[i][j][v] = 1 when quasigroup[i][j] == v (m^3 variables, small for this problem).
    is_value = [[[f"q_{i}_{j}_is_{v}" for v in range(m)] for j in range(m)] for i in range(m)]
    for i in range(m):
        for j in range(m):
            for v in range(m):
                solver.addVariable(is_value[i][j][v], 0, 1)
            # a cell holds exactly one value, and that value is quasigroup[i][j]
            solver.addConstraint([(1, is_value[i][j][v]) for v in range(m)], True, 1, True, 1)
            solver.addConstraint([(v, is_value[i][j][v]) for v in range(1, m)]
                                 + [(-1, quasigroup[i][j])], True, 0, True, 0)

    # each element occurs once in every row, and once in every column (m cells hold m values,
    # so "all different" is the same as "every value appears exactly once")
    for i in range(m):
        for v in range(m):
            solver.addConstraint([(1, is_value[i][j][v]) for j in range(m)], True, 1, True, 1)
            solver.addConstraint([(1, is_value[j][i][v]) for j in range(m)], True, 1, True, 1)

    # QG3.m property: (a*b)*(b*a) = a. If a*b = c and b*a = d, then the entry in row c, column d
    # is a.
    # (when two of the three variables are the same one, their coefficients are added up)
    for a in range(m):
        for b in range(m):
            for c in range(m):
                for d in range(m):
                    coefficients = {}
                    for coefficient, name in ((1, is_value[a][b][c]), (1, is_value[b][a][d]),
                                              (-1, is_value[c][d][a])):
                        coefficients[name] = coefficients.get(name, 0) + coefficient
                    solver.addConstraint([(k, name) for name, k in coefficients.items() if k],
                                         False, 0, True, 1)

    return solver, {"quasigroup": quasigroup}
