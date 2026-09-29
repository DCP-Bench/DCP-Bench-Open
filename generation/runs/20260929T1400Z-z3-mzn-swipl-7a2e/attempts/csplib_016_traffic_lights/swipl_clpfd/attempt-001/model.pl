:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Traffic lights: a four-way junction has four vehicle lights V1..V4 and four
% pedestrian lights P1..P4. Pick a state for each so that every pair of
% neighbouring roads shows one of the safe combinations.
model(Instance, Lights, [lights-Lights]) :-
    Allowed = Instance.allowed_tuples,  % safe (V_i, P_i, V_{i+1}, P_{i+1}); everything else is forbidden
    Vehicle = [V1, V2, V3, V4],
    Pedestrian = [P1, P2, P3, P4],

    % vehicle lights: 0 = red, 1 = red-yellow, 2 = green, 3 = yellow
    Vehicle ins 0..3,
    % pedestrian lights: 0 = red, 1 = green
    Pedestrian ins 0..1,

    % each road and the next one (road 4 is followed by road 1) must show a safe combination
    tuples_in([[V1, P1, V2, P2], [V2, P2, V3, P3], [V3, P3, V4, P4], [V4, P4, V1, P1]], Allowed),

    % reported in the order V1, V2, V3, V4, P1, P2, P3, P4
    append(Vehicle, Pedestrian, Lights).
