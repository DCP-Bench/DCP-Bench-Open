% Csplib 016 traffic lights: a four-way junction with four vehicle lights
% V1..V4 (0=red, 1=red-yellow, 2=green, 3=yellow) and four pedestrian lights
% P1..P4 (0=red, 1=green). For i=1..4 (with V5=V1 and P5=P1) the combination
% (V_i, P_i, V_{i+1}, P_{i+1}) must be one of the safe combinations given in the
% instance; every other combination is disallowed.
% Output: lights = [V1, V2, V3, V4, P1, P2, P3, P4].

:- lib(ic).
:- lib(ic_mdd).

model(Instance, Vars, [lights-Vars]) :-
    memberchk(allowed_tuples-Rows, Instance),
    Vars = [V1, V2, V3, V4, P1, P2, P3, P4],
    [V1, V2, V3, V4] :: 0..3,
    [P1, P2, P3, P4] :: 0..1,

    % The combinations (V_i, P_i, V_{i+1}, P_{i+1}) for i=1..4, with V_5=V_1 and P_5=P_1,
    % must each be one of the safe combinations listed in the instance.
    table([[V1, P1, V2, P2]], Rows),
    table([[V2, P2, V3, P3]], Rows),
    table([[V3, P3, V4, P4]], Rows),
    table([[V4, P4, V1, P1]], Rows).
