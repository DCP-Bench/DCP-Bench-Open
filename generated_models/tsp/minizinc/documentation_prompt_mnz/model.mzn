include "globals.mzn";

% Input data: coordinates of the cities
array[1..12] of tuple2(int,int): locations = [
    (288, 149), (288, 129), (270, 133), (256, 141), (256, 163), (246, 157),
    (236, 169), (228, 169), (228, 148), (220, 164), (212, 172), (204, 159)
];

int: n = length(locations);

% Precompute the distance matrix (Euclidean distance rounded to nearest integer)
array[1..n, 1..n] of int: dist = 
  array2d(1..n, 1..n, 
    [ round(sqrt(
        pow(locations[i].1 - locations[j].1, 2) + 
        pow(locations[i].2 - locations[j].2, 2)
      )) | i,j in 1..n ]);

% Decision variables:
% successor[i] = the city visited immediately after city i in the tour
array[1..n] of var 1..n: successor;

% To eliminate subtours, we use the MTZ formulation with auxiliary variables u
array[1..n] of var 1..n: u;

% Constraints:

% 1) successor forms a permutation (each city has exactly one successor)
constraint all_different(successor);

% 2) MTZ subtour elimination constraints
% u[1] = 1 (start city)
constraint u[1] = 1;
% For all other cities, u[i] in 2..n
constraint forall(i in 2..n) (u[i] >= 2 /\ u[i] <= n);

% For all i != j, enforce MTZ constraints to prevent subtours
constraint forall(i,j in 2..n where i != j) (
    u[i] + 1 <= u[j] \/ successor[i] != j
);

% Objective: minimize total travel distance
var int: travel_distance = sum(i in 1..n)(dist[i, successor[i]]);

solve minimize travel_distance;

output [
    "{",
    "\"travel_distance\": ", show(travel_distance),
    "}"
];