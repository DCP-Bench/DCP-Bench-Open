#!/usr/bin/python3
# Category: csplib
# Source and problem instances: https://www.csplib.org/Problems/prob039/
# Name: The Rehearsal Problem

"""
A concert is to consist of a number of pieces of music of different durations, each involving a different combination
of the members of the orchestra. Players can arrive at rehearsals immediately before the first piece in which they are
involved and depart immediately after the last piece in which they are involved. The problem is to devise an order in
which the pieces can be rehearsed so as to minimize the total time that players are waiting to play, i.e. the total time
when players are present but not currently playing.

Print the optimal rehearsal order (rehearsal_order) in which rehearsal_order[i] is the piece rehearsed in the i-th slot,
as a list of num_pieces integers ranging from 0 to num_pieces - 1.
"""

# Data
num_pieces = 9
num_players = 5
duration = [2, 4, 1, 3, 3, 2, 5, 7, 6]
rehearsal = [[1, 1, 0, 1, 0, 1, 1, 0, 1],
             [1, 1, 0, 1, 1, 1, 0, 1, 0],
             [1, 1, 0, 0, 0, 0, 1, 1, 0],
             [1, 0, 0, 0, 1, 1, 0, 0, 1],
             [0, 0, 1, 0, 1, 1, 1, 1, 0]]
# End of data

# Import libraries
import cpmpy as cp
import json
import numpy as np

# Parameters
duration = cp.cpm_array(duration)
rehearsal = cp.cpm_array(rehearsal)

# Model definition
model = cp.Model()

# Decision Variables
# rehearsal_order[i] is the piece rehearsed in the i-th slot.
rehearsal_order = cp.intvar(0, num_pieces - 1, shape=num_pieces, name="rehearsal_order")
# arrival[p] is the first slot where player p is present.
arrival = cp.intvar(0, num_pieces - 1, shape=num_players, name="arrival")
# departure[p] is the last slot where player p is present.
departure = cp.intvar(0, num_pieces - 1, shape=num_players, name="departure")

# Constraints
# Each piece must be rehearsed exactly once, so the order is a permutation.
model += cp.AllDifferent(rehearsal_order)

# Link arrival and departure times to the rehearsal schedule.
# A player must be present for all pieces they play in.
for p in range(num_players):
    for i in range(num_pieces):
        # is_playing is an expression that is true if player p plays in the piece at slot i.
        is_playing = (rehearsal[p, rehearsal_order[i]] == 1)
        # If a player is playing, they must be present (between their arrival and departure slot).
        model += is_playing.implies((arrival[p] <= i) & (i <= departure[p]))

# Objective: Minimize total waiting time
# Waiting time for a player in a slot is the duration of the piece in that slot
# if the player is present but not playing.
waiting_times = []
for p in range(num_players):
    for i in range(num_pieces):
        is_present = (arrival[p] <= i) & (i <= departure[p])
        is_not_playing = (rehearsal[p, rehearsal_order[i]] == 0)
        is_waiting = is_present & is_not_playing
        # Add the duration of the piece if the player is waiting.
        waiting_times.append(duration[rehearsal_order[i]] * is_waiting)

model.minimize(cp.sum(waiting_times))

# Solve and print
if model.solve():
    solution = {
        'rehearsal_order': rehearsal_order.value().tolist()
    }
    print(json.dumps(solution))
else:
    print("No solution found.")