from pycsp3 import *

# Aircraft landing on one runway: each plane lands at a fixed position in the
# landing sequence, inside its time window, and pays a penalty for landing
# before or after its target time.

n = len(data.target_landing)
earliest = data.earliest_landing
latest = data.latest_landing
target = data.target_landing
pen_before = data.penalty_before
pen_after = data.penalty_after
sep = data.separation_time

horizon = max(latest) + 1
max_shift = horizon

# landing_times[i] is the landing time of plane i
landing_times = VarArray(size=n, dom=range(0, horizon))

# early[i] is how far plane i lands before its target
early = VarArray(size=n, dom=range(0, max_shift))
# tardy[i] is how far plane i lands after its target
tardy = VarArray(size=n, dom=range(0, max_shift))

# total penalty over all planes
total_penalty = Var(dom=range(0, n * max_shift * (max(pen_before + pen_after) + 1)))

satisfy(
    # each plane lands inside its earliest and latest landing time
    [landing_times[i] >= earliest[i] for i in range(n)],
    [landing_times[i] <= latest[i] for i in range(n)],

    # the early shift is the target minus the landing time, when positive
    [early[i] + landing_times[i] >= target[i] for i in range(n)],

    # the late shift is the landing time minus the target, when positive
    [tardy[i] >= landing_times[i] - target[i] for i in range(n)],

    # planes must keep the minimum separation time for the fixed landing order
    [landing_times[j] >= landing_times[i] + sep[i][j]
     for i in range(n) for j in range(i + 1, n)],

    # the total penalty adds the early and late penalties of every plane
    total_penalty == Sum(pen_before[i] * early[i] + pen_after[i] * tardy[i] for i in range(n)),
)

# minimise the total penalty
minimize(total_penalty)
