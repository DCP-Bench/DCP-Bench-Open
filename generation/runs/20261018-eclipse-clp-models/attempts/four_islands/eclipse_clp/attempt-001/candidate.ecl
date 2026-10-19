% Four islands: find the name, export and tourist attraction of each island.
% Islands A, B, C, D are placed as A=0, B=1, C=2, D=3 on the map:
%   (A) -- (B)
%    |      |
%   (C) -- (D)
% Row of a map position is P // 2 (0 = north), column is P mod 2 (0 = west).
% Bridges join islands in the same row or in the same column.
% Outputs: island = [Pwana, Quero, Rayou, Skern], export = [alabaster, bananas,
% coconuts, durian_fruit], attraction = [resort_hotel, ice_skating_rink,
% jai_alai_stadium, koala_preserve]; each value is a map position 0..3.

:- lib(ic).

% A map position P is 2*Row + Col, with Row 0 for the north pair and Col 0 for the west.
% The row and column are separate variables tied to P by a linear equation, since
% ic raises an instantiation fault on // and mod applied to a variable.
coord(P, Row, Col) :-
    Row :: 0..1,
    Col :: 0..1,
    P #= 2*Row + Col.

% X is due south of Y: one row further south, same column.
due_south(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    RX #= RY + 1,
    CX #= CY.

% X is due west of Y: same row, one column further west.
due_west(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    RX #= RY,
    CX #= CY - 1.

% X is due east of Y: same row, one column further east.
due_east(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    RX #= RY,
    CX #= CY + 1.

% X and Y are connected by a north-south bridge: same column, different row.
ns_bridge(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    CX #= CY,
    RX #\= RY.

% X and Y are connected by an east-west bridge: same row, different column.
ew_bridge(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    RX #= RY,
    CX #\= CY.

% X and Y are not connected by a bridge: they lie on a diagonal.
not_bridged(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    RX #\= RY,
    CX #\= CY.

model(_Instance, Vars, Outputs) :-
    Vars = [Pwana, Quero, Rayou, Skern, Alabaster, Bananas, Coconuts, Durian,
            Hotel, Rink, JaiAlai, Koala],
    Vars :: 0..3,
    % Each island has a different name, a different export and a different attraction.
    alldifferent([Pwana, Quero, Rayou, Skern]),
    alldifferent([Alabaster, Bananas, Coconuts, Durian]),
    alldifferent([Hotel, Rink, JaiAlai, Koala]),

    % The island noted for its koala preserve is due south of Pwana.
    due_south(Koala, Pwana),

    % The island with the largest alabaster quarry is due west of Quero.
    due_west(Alabaster, Quero),

    % The island with the resort hotel is due east of the one that exports durian fruit.
    due_east(Hotel, Durian),

    % Skern and the island with the jai alai stadium are connected by a north-south bridge.
    ns_bridge(Skern, JaiAlai),

    % Rayou and the island that exports bananas are connected by an east-west bridge.
    ew_bridge(Rayou, Bananas),

    % The islands noted for the South Pacific's largest ice skating rink and for the
    % jai alai stadium are not connected by a bridge.
    not_bridged(Rink, JaiAlai),

    % 'export' is a prefix operator in ECLiPSe: written as 'export'-[...] inside a list
    % it reads as export(-[...]), so the pairs use the functional form -(Name, Value).
    Outputs = [-('island', [Pwana, Quero, Rayou, Skern]),
               -('export', [Alabaster, Bananas, Coconuts, Durian]),
               -('attraction', [Hotel, Rink, JaiAlai, Koala])].
