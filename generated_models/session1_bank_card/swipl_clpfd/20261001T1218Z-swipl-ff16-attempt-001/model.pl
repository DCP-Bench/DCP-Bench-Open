:- use_module(library(clpfd)).

% Bank card: the card has a 4 digit PIN abcd. No two digits are the same, the
% 2-digit number cd is 3 times the 2-digit number ab, and the 2-digit number da
% is 2 times the 2-digit number bc. Find the PIN. The problem has no instance
% data.
model(_Instance, Vars, [a-A, b-B, c-C, d-D]) :-
    Vars = [A, B, C, D],
    Vars ins 0..9,

    % no two digits are the same
    all_distinct(Vars),

    % the 2-digit number cd is 3 times the 2-digit number ab
    10 * C + D #= 3 * (10 * A + B),

    % the 2-digit number da is 2 times the 2-digit number bc
    10 * D + A #= 2 * (10 * B + C).
