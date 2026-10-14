% Travelling salesman: find the shortest closed route that visits every city
% exactly once and returns to the start. The distance between two cities is the
% Euclidean distance between their locations rounded to an integer.
include "globals.mzn";

array[int, int] of int: locations;  % (x, y) of each city
int: n = card(index_set_1of2(locations));

% rounded Euclidean distance between every pair of cities
array[1..n, 1..n] of int: distance = array2d(1..n, 1..n,
    [round(sqrt(int2float((locations[i, 1] - locations[j, 1]) * (locations[i, 1] - locations[j, 1])
                          + (locations[i, 2] - locations[j, 2]) * (locations[i, 2] - locations[j, 2]))))
     | i in 1..n, j in 1..n]);

% successor[i] = the city visited right after city i; together they form one circuit
array[1..n] of var 1..n: successor;
constraint circuit(successor);

% travel_distance = length of the route, to be minimised
var int: travel_distance = sum(i in 1..n) (distance[i, successor[i]]);
var int: objective = travel_distance;
solve minimize objective;

output ["{\"travel_distance\": ", show(travel_distance), "}"];
