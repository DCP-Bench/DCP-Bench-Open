% Send More Money: assign a distinct digit 0..9 to each letter s, e, n, d, m, o, r, y
% so that SEND + MORE = MONEY holds, with the first letter of each word not zero.

:- lib(ic).

model(_Instance, [S, E, N, D, M, O, R, Y], [s-S, e-E, n-N, d-D, m-M, o-O, r-R, y-Y], none) :-
    % each letter represents a unique digit from 0 to 9
    [S, E, N, D, M, O, R, Y] :: 0..9,
    alldifferent([S, E, N, D, M, O, R, Y]),

    % the first letter of each word cannot be zero
    S #\= 0,
    M #\= 0,

    % the equation SEND + MORE = MONEY
    1000*S + 100*E + 10*N + D + 1000*M + 100*O + 10*R + E
        #= 10000*M + 1000*O + 100*N + 10*E + Y.
