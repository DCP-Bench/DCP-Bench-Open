Take a rack cabinet. Let's say, there are a number of 1U devices, maybe servers, routers and whatnot.
Devices must be connected by cables: probably
twisted pair or whatever network engineers are using today. Some devices must be
connected by several cables.

Each device takes one position in the rack, and neighbouring positions are one unit apart. A cable between
two devices is as long as the distance between their positions, so connecting them by `k` cables costs `k`
times that distance.

The problem: how we can place these devices in such an order, so that sum
of all cable lengths would be as short as possible?

Print the optimal sum of all cable lengths (final_sum).
