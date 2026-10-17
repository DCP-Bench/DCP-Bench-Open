# Guards and apples: a boy passes num_gates gates. At each gate he bribes the guard with
# half of his apples plus one, giving an integer number of apples. After the last gate he
# gives the girl one apple and has none left. Output apples: the count before each gate,
# then the count after the last gate, so num_gates + 1 numbers.
import mip


def build(instance):
    n = instance["num_gates"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # apples[i] is the count before gate i (i < n), apples[n] the count after the last gate.
    # Every count only shrinks, and the recurrence below bounds the first count by 2^(n+2).
    ub = 2 ** (n + 2)
    apples = [model.add_var(f"apples_{i}", lb=0, ub=ub, var_type=mip.INTEGER)
              for i in range(n + 1)]

    # gate i: the bribe is half of the apples plus one, so the apples before it are even
    # and the bribe is an integer number of apples.
    halves = [model.add_var(f"half_{i}", lb=0, ub=ub, var_type=mip.INTEGER)
              for i in range(n)]
    for i in range(n):
        # the apples before gate i are twice their half
        model.add_constr(apples[i] == 2 * halves[i])
        # what is left after paying the bribe (half plus one)
        model.add_constr(apples[i + 1] == halves[i] - 1)

    # after the last gate he gives the girl one apple and has no apples left
    # (the one apple given is the one he keeps after the last gate)
    model.add_constr(apples[n] == 1)

    # no objective: the task is to find the counts that satisfy the gates
    return model, {"apples": apples}
