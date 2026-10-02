:- use_module(library(clpfd)).

% Hanging weights: thirteen weights A..M hang from a system of bars. Each
% weight is a different integer from 1 to 13. Find the weights for which every
% bar balances: the weights on either side of a pivot must be equal when
% weighted by their distance from the pivot, and a bar hanging beneath another
% counts as a single weight equal to its total. The problem has no instance
% data; the bar equations below are the ones the reference derives from the
% diagram in the statement, one per bar.
model(_Instance, Vars, [a-A, b-B, c-C, d-D, e-E, f-F, g-G, h-H, i-I, j-J, k-K, l-L, m-M]) :-
    Vars = [A, B, C, D, E, F, G, H, I, J, K, L, M],

    % each weight is a different integer from 1 to 13
    length(Vars, N),
    Vars ins 1..N,
    all_distinct(Vars),

    % the bar holding A and B balances
    4 * A #= B,

    % the bottom right bar balances: 5*C = D
    5 * C #= D,

    % the bar holding E and F balances
    3 * E #= 2 * F,

    % the bar above the C-D bar balances: 3*G = 2*(C+D), where the C-D bar
    % counts as one weight C+D
    3 * G #= 2 * (C + D),

    % the bar with J and the A-B bar on one side, and K and the G-C-D bar on the
    % other, balances
    3 * (A + B) + 2 * J #= K + 2 * (G + C + D),

    % the bar with H on one side, and I and the E-F bar on the other, balances
    3 * H #= 2 * (E + F) + 3 * I,

    % the bar with the H-I group on one side, and L and M on the other, balances
    H + I + E + F #= L + 4 * M,

    % the top bar balances: the group of L, M, H, I, E, F against the group of
    % J, K, G, A, B, C, D
    4 * (L + M + H + I + E + F) #= 3 * (J + K + G + A + B + C + D).
