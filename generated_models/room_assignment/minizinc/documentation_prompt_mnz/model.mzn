include "globals.mzn";

% Input data
int: max_rooms = 5;
int: num_requests = 4;

% Dates converted to integer days for easier comparison
% Using a simple mapping: 2024-05-01 -> day 1, 2024-05-02 -> day 2, etc.
array[1..num_requests] of int: start = [1, 2, 3, 4];
array[1..num_requests] of int: end_ = [5, 6, 7, 8];

% Preassigned rooms: -1 means no pre-assignment
array[1..num_requests] of int: preassigned_room = [3, -1, -1, -1];

% Decision variables
% room_assignments[i] is the room assigned to request i (1..max_rooms)
array[1..num_requests] of var 1..max_rooms: room_assignments;

% Constraints

% Enforce pre-assigned rooms
constraint
  forall(i in 1..num_requests) (
    if preassigned_room[i] != -1 then
      room_assignments[i] = preassigned_room[i]
    else
      true
    endif
  );

% No overlapping requests in the same room
constraint
  forall(i, j in 1..num_requests where i < j) (
    % If requests i and j overlap in time, they cannot share the same room
    (end_[i] <= start[j] \/ end_[j] <= start[i]) \/ (room_assignments[i] != room_assignments[j])
  );

solve satisfy;

output [
  "{",
  "\"room_assignments\": ", show(room_assignments),
  "}"
];