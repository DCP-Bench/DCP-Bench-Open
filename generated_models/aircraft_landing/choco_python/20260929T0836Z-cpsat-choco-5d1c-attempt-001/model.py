# Aircraft landing with a fixed landing order: give every aircraft a landing
# time inside its window so that consecutive landings keep the required
# separation, minimising the penalty for landing before or after the target.
from pychoco.model import Model


def build(instance):
    earliest = instance["earliest_landing"]  # start of each aircraft's window
    latest = instance["latest_landing"]  # end of each aircraft's window
    target = instance["target_landing"]  # preferred landing time
    penalty_before = instance["penalty_before"]  # cost per time unit landing early
    penalty_after = instance["penalty_after"]  # cost per time unit landing late
    separation = instance["separation_time"]  # minimum gap between two landings
    n = len(earliest)
    horizon = max(latest)

    model = Model()

    landing_times = [model.intvar(0, horizon, name=f"landing_{i}") for i in range(n)]
    # how far before / after its target each aircraft lands
    earliness = [model.intvar(0, horizon, name=f"earliness_{i}") for i in range(n)]
    lateness = [model.intvar(0, horizon, name=f"lateness_{i}") for i in range(n)]

    for i in range(n):
        # each aircraft lands inside its time window
        model.arithm(landing_times[i], ">=", earliest[i]).post()
        model.arithm(landing_times[i], "<=", latest[i]).post()
        # the deviation from the target is split into earliness and lateness;
        # the positive penalties make the solver keep one of the two at zero
        model.scalar([landing_times[i], lateness[i], earliness[i]], [1, -1, 1], "=", target[i]).post()

    # the landing order is fixed as the aircraft index order (as the problem
    # states), so aircraft j lands at least separation[i][j] after aircraft i
    for i in range(n):
        for j in range(i + 1, n):
            model.arithm(landing_times[j], "-", landing_times[i], ">=", separation[i][j]).post()

    # total penalty for early and late landings (Choco minimises one variable)
    total_penalty = model.intvar(0, horizon * (sum(penalty_before) + sum(penalty_after)), name="total_penalty")
    model.scalar(earliness + lateness, penalty_before + penalty_after, "=", total_penalty).post()

    return model, {"landing_times": landing_times, "total_penalty": total_penalty}, ("minimize", total_penalty)
