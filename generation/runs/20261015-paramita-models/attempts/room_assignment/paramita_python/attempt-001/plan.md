# Plan: room_assignment, attempt 001

- Each request is assigned to exactly one room -> one-hot x[i][r] per request and room, sum(x[i]) == 1
- A request with a pre-assigned room keeps it -> x[i][pre] as a required literal (for preassigned_room_data >= 0)
- A room serves one request at a time; requests overlap when start_i < end_j and start_j < end_i (end date exclusive, so back-to-back requests do not overlap) -> per overlapping pair and room: ~(x[i][r] & x[j][r])
- Output room_assignments -> per request, sum(r * x[i][r]) over the rooms (integer expression)
- Satisfaction problem, no objective
