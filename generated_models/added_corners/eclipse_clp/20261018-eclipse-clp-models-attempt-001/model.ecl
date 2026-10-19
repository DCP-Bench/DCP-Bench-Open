% Added corners: enter the digits 1 through 8 in the circles and squares
% such that the number in each square is equal to the sum of the numbers
% in the adjoining circles. Outputs are the 8 positions, read left to right,
% top to bottom: TL C, TM F, TR C, ML F, MR F, BL C, BM F, BR C.

:- lib(ic).

model(_Instance, Vars, [positions-Ps]) :-
    Ps = [P1, P2, P3, P4, P5, P6, P7, P8],
    Vars = Ps,

    % Enter the digits 1 through 8 in the circles and squares.
    Ps :: 1..8,
    alldifferent(Ps),

    % The number in each square is equal to the sum of the numbers in the
    % adjoining circles.
    P2 #= P1 + P3,
    P4 #= P1 + P6,
    P5 #= P3 + P8,
    P7 #= P6 + P8.
