"""Feasibility check for addition cryptarithms. A solution is {"digits": {"S": 9, ...}}."""


def feasible(instance, solution):
    words = instance["addends"] + [instance["sum"]]
    letters = sorted(set("".join(words)))
    d = solution.get("digits")
    if not isinstance(d, dict) or sorted(d) != letters:
        return [f"'digits' must map exactly the letters {letters} to digits"]
    if any(type(v) is not int or not 0 <= v <= 9 for v in d.values()):
        return ["every digit must be an integer in 0..9"]
    errors = []
    if len(set(d.values())) != len(d):
        errors.append("two letters share a digit")
    errors += [f"{w} has a leading zero" for w in words if len(w) > 1 and d[w[0]] == 0]

    def value(w):
        return int("".join(str(d[ch]) for ch in w))

    total = sum(value(w) for w in instance["addends"])
    if total != value(instance["sum"]):
        errors.append(f"addends sum to {total}, not {value(instance['sum'])}")
    return errors
