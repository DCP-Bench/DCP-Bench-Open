You are given an 8 pint bucket of water, and two empty buckets which can contain 5 and 3 pints respectively.
You are required to divide the water into two by pouring water between buckets (that is, to end up with
4 pints in the 8 pint bucket, and 4 pints in the 5 pint bucket).

This task is to find the minimum number of transfers of water between buckets to reach the goal.

Print the minimum number of transfers (cost) and the sequence of states (sequence). The sequence must
be a list of exactly MAX_STEPS integer lists. After the goal state is reached, the remainder of the list must be
padded with the padding states, e.g. [-1, -1, -1].
