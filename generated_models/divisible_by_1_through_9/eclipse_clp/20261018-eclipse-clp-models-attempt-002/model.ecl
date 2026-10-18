% Model for divisible_by_1_through_9: find a 10 digit number that uses each of
% the digits 0 to 9 exactly once and where the number formed by the first n
% digits of the number is divisible by n. Output: number (the full 10 digit number).

:- lib(ic).

model(_Instance, Digits, [number-Number]) :-
    % a number that uses each of the digits 0 to 9 exactly once
    length(Digits, 10),
    Digits :: 0..9,
    alldifferent(Digits),
    % a 10 digit number has a nonzero leading digit
    Digits = [First|_],
    First #\= 0,
    % the number formed by the first n digits of the number is divisible by n
    prefix_rules(1, 10, Digits),
    % the number itself, read from left to right
    place_values(Digits, 9, Terms),
    Number :: 0..9999999999,
    Number #= sum(Terms).

% The prefix of length N, read as a number, is divisible by N. Its value is
% sum of 10^(N-i) * D_i. Reduced modulo N, each weight 10^(N-i) mod N is a
% ground integer, so the rule is the linear equation sum(W_i * D_i) = N * Q
% with Q a fresh quotient in a bounded range.
prefix_rules(N, Max, Digits) :-
    ( N > Max ->
        true
    ;   length(Prefix, N),
        append(Prefix, _, Digits),
        weights(N, 1, Ws),
        weighted(Ws, Prefix, Terms),
        wsum(Ws, 0, SumW),
        MaxQ is (9 * SumW) // N,
        Q :: 0..MaxQ,
        sum(Terms) #= N * Q,
        N1 is N + 1,
        prefix_rules(N1, Max, Digits)
    ).

% weights(N, I, Ws): Ws holds 10^(N-I) mod N, ..., 10^0 mod N for the
% positions I..N of a prefix of length N.
weights(N, I, Ws) :-
    ( I > N ->
        Ws = []
    ;   E is N - I,
        W is 10^E mod N,
        I1 is I + 1,
        Ws = [W|Ws1],
        weights(N, I1, Ws1)
    ).

weighted([], [], []).
weighted([W|Ws], [D|Ds], [W*D|Ts]) :-
    weighted(Ws, Ds, Ts).

wsum([], S, S).
wsum([W|Ws], A, S) :-
    A1 is A + W,
    wsum(Ws, A1, S).

% place values of the 10 digits: digit i has weight 10^(10-i)
place_values([], _, []).
place_values([D|Ds], E, [P*D|Ts]) :-
    P is 10^E,
    E1 is E - 1,
    place_values(Ds, E1, Ts).
