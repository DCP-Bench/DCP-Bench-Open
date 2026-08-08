
include "globals.mzn";

% Input data
int: deck_width = 5;
int: deck_length = 5;
int: n_containers = 3;
array[1..n_containers] of int: width  = [5, 2, 3];
array[1..n_containers] of int: length = [1, 4, 4];

% Decision variables: positions of each container
array[1..n_containers] of var 0..deck_width:  left;
array[1..n_containers] of var 0..deck_length: bottom;
array[1..n_containers] of var 0..deck_width:  right;
array[1..n_containers] of var 0..deck_length: top;

% Define right and top in terms of left/bottom and size
constraint forall(i in 1..n_containers) (
    right[i] = left[i] + width[i]
    /\ top[i]   = bottom[i] + length[i]
);

% Rectangles must lie inside the deck
constraint forall(i in 1..n_containers) (
    left[i]  >= 0
    /\ right[i]  <= deck_width
    /\ bottom[i] >= 0
    /\ top[i]     <= deck_length
);

% No-overlap constraint using global diffn
constraint diffn(
    [left[i]   | i in 1..n_containers],
    [bottom[i] | i in 1..n_containers],
    [width[i]  | i in 1..n_containers],
    [length[i] | i in 1..n_containers]
);

% Sequential loading constraints: each container i must touch
% something to its west (left edge) and north (top edge)
constraint forall(i in 1..n_containers) (
    let {
        % West contact: either against west wall or against a previously placed container
        var bool: west_contact = 
            (left[i] = 0)
            \/ exists(j in 1..i-1) (
                 left[i] = right[j]
                 /\ bottom[i] < top[j]
                 /\ top[i]    > bottom[j]
            ),
        % North contact: either against north wall or against a previously placed container
        var bool: north_contact =
            (top[i] = deck_length)
            \/ exists(j in 1..i-1) (
                 top[i] = bottom[j]
                 /\ left[i]  < right[j]
                 /\ right[i] > left[j]
            )
    } in
    west_contact /\ north_contact
);

solve satisfy;

output [
    "{",
    join(",", [
      "\"" ++ "left" ++ "\": [" ++ join(",", [show(left[i])  | i in 1..n_containers]) ++ "]",
      "\"" ++ "right" ++ "\": [" ++ join(",", [show(right[i]) | i in 1..n_containers]) ++ "]",
      "\"" ++ "top" ++ "\": [" ++ join(",", [show(top[i])   | i in 1..n_containers]) ++ "]",
      "\"" ++ "bottom" ++ "\": [" ++ join(",", [show(bottom[i])| i in 1..n_containers]) ++ "]"
    ]),
    "}"
];
