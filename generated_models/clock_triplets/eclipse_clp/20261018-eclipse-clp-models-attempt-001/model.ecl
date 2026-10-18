% Clock triplets: rearrange the numbers 1 to 12 on the face of a clock so that
% no triplet of adjacent numbers has a sum higher than 21. The clock is circular,
% so the triplets wrap around from position 12 back to position 1.
% Output x is the list of the 12 numbers in clock order.

:- lib(ic).

model(_Instance, [A, B, C, D, E, F, G, H, I, J, K, L], [x-[A, B, C, D, E, F, G, H, I, J, K, L]]) :-
    % the twelve numbers on the clock face are the integers 1 to 12, each used once
    [A, B, C, D, E, F, G, H, I, J, K, L] :: 1..12,
    alldifferent([A, B, C, D, E, F, G, H, I, J, K, L]),

    % no triplet of adjacent numbers sums to more than 21 (all twelve triplets, wrapping around)
    A + B + C #=< 21,
    B + C + D #=< 21,
    C + D + E #=< 21,
    D + E + F #=< 21,
    E + F + G #=< 21,
    F + G + H #=< 21,
    G + H + I #=< 21,
    H + I + J #=< 21,
    I + J + K #=< 21,
    J + K + L #=< 21,
    K + L + A #=< 21,
    L + A + B #=< 21.
