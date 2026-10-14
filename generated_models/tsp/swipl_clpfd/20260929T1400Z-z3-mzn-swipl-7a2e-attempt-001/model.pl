:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Travelling salesman: find the shortest closed route that visits every city
% exactly once and returns to the start. The distance between two cities is the
% Euclidean distance between their locations rounded to an integer.
model(Instance, [Total|Successor], [travel_distance-Total], min(Total)) :-
    Locations = Instance.locations,   % (x, y) of each city
    length(Locations, N),

    % the rounded Euclidean distance from every city to every other city
    maplist({Locations}/[[X1, Y1], Row]>>maplist({X1, Y1}/[[X2, Y2], D]>>(
                  D is round(sqrt((X1 - X2) * (X1 - X2) + (Y1 - Y2) * (Y1 - Y2)))), Locations, Row),
            Locations, Distances),

    % Successor[i] = the city visited right after city i (numbered from 1);
    % together they form one circuit
    length(Successor, N),
    Successor ins 1..N,
    circuit(Successor),

    % the distance travelled from city i to its successor, read from row i of the
    % distance matrix with element/3
    maplist([Row, City, Leg]>>element(City, Row, Leg), Distances, Successor, Legs),

    % the length of the route, to be minimised
    append(Distances, AllDistances),
    sum_list(AllDistances, DistanceSum),
    Total in 0..DistanceSum,
    sum(Legs, #=, Total).
