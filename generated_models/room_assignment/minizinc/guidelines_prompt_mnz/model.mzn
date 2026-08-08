
% Room assignment problem in Minizinc

% Input data
int: max_rooms = 5;
int: n = 4;
% For simplicity map dates in May 2024 to their day numbers
array[1..n] of int: start_day = [1, 2, 3, 4];
array[1..n] of int: end_day   = [5, 6, 7, 8];
array[1..n] of int: preassigned_room = [3, -1, -1, -1]; 

% Decision variables: room assigned to each request
array[1..n] of var 1..max_rooms: room_assignments;

% Apply pre-assignment constraints
constraint
  forall(i in 1..n where preassigned_room[i] != -1) (
    room_assignments[i] = preassigned_room[i]
  );

% No two overlapping requests in the same room
constraint
  forall(i, j in 1..n where i < j) (
    % intervals [start_day[i], end_day[i]] and [start_day[j], end_day[j]]
    % overlap iff start_i <= end_j /\ start_j <= end_i
    (start_day[i] <= end_day[j] /\ start_day[j] <= end_day[i])
      -> room_assignments[i] != room_assignments[j]
  );

solve satisfy;

% Output in JSON format
output [
  "{",
    "\"room_assignments\":[" ++
      join(",", [show(room_assignments[i]) | i in 1..n])
    ++ "]",
  "}"
];
