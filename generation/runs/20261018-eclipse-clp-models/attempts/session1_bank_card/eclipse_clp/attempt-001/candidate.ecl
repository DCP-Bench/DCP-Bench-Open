% Bank card PIN puzzle (session1_bank_card): find the 4-digit PIN abcd
% with the printed digits a, b, c, d.

:- lib(ic).

model(_Instance, [A, B, C, D], [a-A, b-B, c-C, d-D]) :-
    % My bank card has a 4 digit pin, abcd.
    [A, B, C, D] #:: 1..9,

    % no two digits are the same
    alldifferent([A, B, C, D]),

    % the 2-digit number cd is 3 times the 2-digit number ab
    10 * C + D #= 3 * (10 * A + B),

    % the 2-digit number da is 2 times the 2-digit number bc
    10 * D + A #= 2 * (10 * B + C).
