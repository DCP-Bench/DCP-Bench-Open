#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/room_assignment.ipynb

"""
The room assignment problem involves assigning a set of requests to a limited number of rooms such that each
request is assigned to one room for its entire duration. Some requests may already have a room pre-assigned. The main
constraint is that a room can only serve one request at a time, meaning no overlapping requests can be assigned to
the same room.

Print the room assignment for each request (room_assignments) as a list of integers ranging from 0 to max_rooms - 1.
"""

# Data
max_rooms = 5  # Maximum number of rooms available
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]  # Start date of the requests
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]  # End date of the requests
preassigned_room_data = [3, -1, -1, -1]  # Room 3 pre-assigned for the first request, -1 for no pre-assignment. So, the second, third, and fourth requests have no pre-assigned rooms.
# End of data

# Import libraries
import pandas as pd
from cpmpy import *
import numpy as np
import json

# Parameters
data = {
    "start": pd.to_datetime(start_data),
    "end": pd.to_datetime(end_data),
    # convert 0 to NaN
    "room": [r if r != -1 else np.nan for r in preassigned_room_data]
}
df = pd.DataFrame(data)


def model_rooms(df, max_rooms):
    n_requests = len(df)

    # All requests must be assigned to one out of the rooms (same room during entire period).
    requestvars = intvar(0, max_rooms - 1, shape=(n_requests,))

    m = Model()

    # Some requests already have a room pre-assigned
    for idx, row in df.iterrows():
        if not pd.isna(row['room']):
            m += (requestvars[idx] == int(row['room']))

    # A room can only serve one request at a time.
    # <=> requests on the same day must be in different rooms
    for day in pd.date_range(min(df['start']), max(df['end'])):
        overlapping = df[(df['start'] <= day) & (day < df['end'])]
        if len(overlapping) > 1:
            m += AllDifferent(requestvars[overlapping.index])

    return m, requestvars


# Example usage
model, room_assignments = model_rooms(df, max_rooms)
model.solve()

# Print
solution = {"room_assignments": room_assignments.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
