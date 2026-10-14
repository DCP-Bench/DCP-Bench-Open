from pycsp3 import *

n = data.n
devices = data.devices
cables = data.cable_struct

# the position of each device in the rack, positions 0 to n-1
position = VarArray(size=n, dom=range(n))
satisfy(
    # each device occupies a different place in the rack
    AllDifferent(position),
)

# the total of all cable lengths, where each cable length is the distance between its two devices
total_bound = sum(count for _, _, count in cables) * (n - 1)
final_sum = Var(dom=range(total_bound + 1))
satisfy(
    # the sum of all cable lengths is the total length
    final_sum == Sum(count * abs(position[devices.index(a)] - position[devices.index(b)]) for a, b, count in cables),
)

# the sum of all cable lengths is as short as possible
minimize(final_sum)
