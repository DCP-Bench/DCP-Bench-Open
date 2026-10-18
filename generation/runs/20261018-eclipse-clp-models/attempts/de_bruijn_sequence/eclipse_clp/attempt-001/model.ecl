% de Bruijn sequence: print the de Bruijn sequence of a given order n on a
% size-k alphabet (base k) as a list of integers. The sequence is cyclic and
% has length k^n; every possible length-n string on the alphabet occurs
% exactly once as a substring.

:- lib(ic).
:- lib(listut).

model(Instance, Xs, [de_bruijn-Xs], none) :-
    memberchk(base-B, Instance),
    memberchk(n-N, Instance),
    L is B^N,
    length(Xs, L),
    Xs :: 0..B-1,

    % every possible length-n string on the alphabet occurs exactly once as a
    % substring of the cyclic sequence: each length-n window (read cyclically)
    % gets a code in base B, and the codes are all different
    length(Codes, L),
    Codes :: 0..L-1,
    alldifferent(Codes),
    (   for(I, 0, L-1),
        foreach(C, Codes),
        param(Xs, L, B, N)
    do
        window_code(Xs, L, B, N, I, C)
    ),

    % the sequence is cyclic and has length k^n, so there is no further
    % condition on the window starts
    true.

% window_code(+Xs, +L, +B, +N, +I, -C): C is the base-B value of the length-N
% window of the cyclic sequence Xs that starts at position I (0-based).
window_code(Xs, L, B, N, I, C) :-
    (   for(J, 0, N-1),
        foreach(X*P, Terms),
        param(Xs, L, B, N, I)
    do
        K is (I + J) mod L,
        nth0(K, Xs, X),
        P is B^(N-1-J)
    ),
    C #= sum(Terms).
