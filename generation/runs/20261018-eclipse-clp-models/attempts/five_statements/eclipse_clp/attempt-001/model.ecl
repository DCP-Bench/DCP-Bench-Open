% Problem: five_statements
% Determine which of the following statements is true.
%   1. Exactly one of these statements is false.
%   2. Exactly two of these statements are false.
%   3. Exactly three of these statements are false.
%   4. Exactly four of these statements are false.
%   5. Exactly five of these statements are false.
% Output statements: one 0/1 value per statement (1 = true), in input order.

:- lib(ic).

model(_Instance, [S1, S2, S3, S4, S5], [statements-[S1, S2, S3, S4, S5]]) :-
    [S1, S2, S3, S4, S5] :: 0..1,
    % F is the number of false statements: a statement is false when its value is 0.
    F :: 0..5,
    F #= 5 - S1 - S2 - S3 - S4 - S5,

    % Statement i is true exactly when exactly i of these statements are false.
    % Exactly one of these statements is false.
    S1 #= (F #= 1),
    % Exactly two of these statements are false.
    S2 #= (F #= 2),
    % Exactly three of these statements are false.
    S3 #= (F #= 3),
    % Exactly four of these statements are false.
    S4 #= (F #= 4),
    % Exactly five of these statements are false.
    S5 #= (F #= 5).
