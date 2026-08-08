include "globals.mzn";

% Input data
int: deck_width = 5;
int: deck_length = 5;
int: n_containers = 3;
array[1..n_containers] of int: width = [5, 2, 3];
array[1..n_containers] of int: length = [1, 4, 4];
array[1..n_containers] of int: classes = [1, 1, 1];
int: n_classes = 2; % from separation matrix size
array[1..n_classes, 1..n_classes] of int: separation = [
    |0, 0|
    |0, 0|
];

% Decision variables: positions of containers on the deck
% left[i], bottom[i] are coordinates of the bottom-left corner of container i
array[1..n_containers] of var 0..deck_width: left;
array[1..n_containers] of var 0..deck_length: bottom;

% Derived variables for right and top edges
array[1..n_containers] of var 0..deck_width: right;
array[1..n_containers] of var 0..deck_length: top;

% Define right and top edges based on left, bottom, width, and length
constraint forall(i in 1..n_containers) (
    right[i] = left[i] + width[i] /\
    top[i] = bottom[i] + length[i]
);

% Containers must be within deck boundaries
constraint forall(i in 1..n_containers) (
    right[i] <= deck_width /\
    top[i] <= deck_length
);

% No overlapping constraints between containers
constraint forall(i, j in 1..n_containers where i < j) (
    (right[i] <= left[j]) \/
    (right[j] <= left[i]) \/
    (top[i] <= bottom[j]) \/
    (top[j] <= bottom[i])
);

% Separation constraints between classes
% For each pair of containers i, j with classes c_i, c_j, enforce minimum separation
constraint forall(i, j in 1..n_containers where i < j) (
    let {
        int: sep = separation[classes[i], classes[j]]
    } in
    if sep > 0 then
        % Enforce separation either horizontally or vertically
        (left[i] + width[i] + sep <= left[j]) \/
        (left[j] + width[j] + sep <= left[i]) \/
        (bottom[i] + length[i] + sep <= bottom[j]) \/
        (bottom[j] + length[j] + sep <= bottom[i])
    else
        true
    endif
);

% Loading sequence constraints:
% Each container after the first must touch another container or deck wall to the north and west
% Touching means: 
% - For north: bottom[i] == top[j] for some j or bottom[i] == 0 (deck wall)
% - For west: left[i] == right[j] for some j or left[i] == 0 (deck wall)
%
% The loading sequence is the order of containers 1..n_containers
constraint forall(i in 2..n_containers) (
    % Touch north: bottom[i] == 0 or bottom[i] == top[j] for some j != i
    (bottom[i] == 0 \/
     exists(j in 1..n_containers where j != i) (bottom[i] == top[j] /\
        % Also horizontal overlap to ensure touching along some part
        not (right[i] <= left[j] \/ left[i] >= right[j])
     )
    ) /\
    % Touch west: left[i] == 0 or left[i] == right[j] for some j != i
    (left[i] == 0 \/
     exists(j in 1..n_containers where j != i) (left[i] == right[j] /\
        % Also vertical overlap to ensure touching along some part
        not (top[i] <= bottom[j] \/ bottom[i] >= top[j])
     )
    )
);

solve satisfy;

output [
    "{",
    join(",", [
        "\"left\": " ++ show(left),
        "\"right\": " ++ show(right),
        "\"top\": " ++ show(top),
        "\"bottom\": " ++ show(bottom)
    ]),
    "}"
];