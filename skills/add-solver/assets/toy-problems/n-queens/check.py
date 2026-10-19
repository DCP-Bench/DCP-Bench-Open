"""Feasibility check for n-queens. A solution is {"queens": [c_0, ..., c_{n-1}]}."""


def feasible(instance, solution):
    n = instance["n"]
    q = solution.get("queens")
    if not isinstance(q, list) or len(q) != n:
        return [f"'queens' must be a list of {n} column indices"]
    if any(type(c) is not int or not 0 <= c < n for c in q):
        return [f"every column must be an integer in 0..{n - 1}"]
    errors = []
    for i in range(n):
        for j in range(i + 1, n):
            if q[i] == q[j]:
                errors.append(f"rows {i} and {j} share column {q[i]}")
            elif abs(q[i] - q[j]) == j - i:
                errors.append(f"rows {i} and {j} share a diagonal")
    return errors
