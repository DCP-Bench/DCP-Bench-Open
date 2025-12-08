#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob010_social_golfers.py
# Source description and problem instances: https://www.csplib.org/Problems/prob010/

"""
The coordinator of a local golf club has come to you with the following problem. In their club, there are 32 social
golfers, each of whom play golf once a week, and always in groups of 4. They would like you to come up with a schedule
of play for these golfers, such that no golfer plays in the same group as any other golfer on more than one occasion.

Print the assignments of golfers to groups for each week (assign) as a list of lists of integers - 0-indexed; assign[i][j]
is the group number of golfer i in week j.
"""

# Data
n_weeks = 4  # Number of weeks
n_groups = 3  # Number of groups
group_size = 3  # Size of each group
# End of data

# Import libraries
from cpmpy import *
from cpmpy.expressions.utils import all_pairs
import numpy as np
import json


def social_golfers(n_weeks, n_groups, group_size):

    n_golfers = n_groups * group_size
    golfers = np.arange(n_golfers)
    weeks = np.arange(n_weeks)
    groups = np.arange(n_groups)

    # Possible configurations
    assign = intvar(0, n_groups - 1, shape=(n_golfers, n_weeks), name="assign")

    model = Model()

    # C1: Each group has exactly group_size players
    for gr in groups:
        for w in weeks:
            model += sum(assign[:, w] == gr) == group_size

    # C2: Each pair of players only meets at most once
    for g1, g2 in all_pairs(golfers):
        model += sum(assign[g1] == assign[g2]) <= 1

    # SBSA: Symmetry-breaking by selective assignment
    # On the first week, the first group_size golfers play in group 1, the
    # second group_size golfers play in group 2, etc. On the second week,
    # golfer 1 plays in group 1, golfer 2 plays in group 2, etc.
    # model += [assign[:, 0] == (golfers // group_size)]

    # <SYMMETRY_BREAKING_CONSTRAINT_START>
    # for g in golfers:
    #     if g < group_size:
    #         model += [assign[g, 1] == g]

    # # First golfer always in group 0
    # model += [assign[0, :] == 0]
    # <SYMMETRY_BREAKING_CONSTRAINT_END>

    return model, assign

# Example usage
model, assign = social_golfers(n_weeks, n_groups, group_size)

# Solve
model.solve()

# Print
solution = {
    "assign": assign.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
