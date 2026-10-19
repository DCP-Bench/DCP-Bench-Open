# Covering problem (covering_opl): select a set of workers that performs all tasks
# at minimum total hiring cost. Each worker can perform certain tasks and has a
# hiring cost. Output: total cost, and per worker whether it is hired.
import mip


def build(instance):
    nb_workers = instance["nb_workers"]
    num_tasks = instance["num_tasks"]
    cost = instance["Cost"]
    qualified = instance["Qualified"]  # one list per task, 1-based worker ids

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    hire = [m.add_var(f"hire_{i}", var_type=mip.BINARY) for i in range(nb_workers)]
    total_cost = m.add_var("total_cost", lb=0, ub=sum(cost), var_type=mip.INTEGER)

    # The total cost is the sum of the hiring costs of the selected workers.
    m += total_cost == mip.xsum(cost[i] * hire[i] for i in range(nb_workers))

    # Ensure that all tasks are performed: each task needs at least one hired
    # worker among the workers qualified for it.
    for t in range(num_tasks):
        m += mip.xsum(hire[w - 1] for w in qualified[t]) >= 1

    m.objective = total_cost

    return m, {"total_cost": total_cost, "workers": hire}
