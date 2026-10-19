% Problem cur_num: The number 48 has this peculiarity, that if you add 1 to it
% the result is a square number, and if you add 1 to its half, you also get a
% square number. Print another number with this peculiarity (peculiar) between
% 1 and 10000.

:- lib(ic).

model(_Instance, [Peculiar, Half, A, B], [peculiar-Peculiar], none) :-
    % The number 48 has this peculiarity, that if you add 1 to it the result
    % is a square number, and if you add 1 to its half, you also get a square number.
    Peculiar :: 1..10000,
    Half :: 1..5000,
    A :: 1..100,
    B :: 1..70,
    % Print another number with this peculiarity: not 48 itself.
    Peculiar #\= 48,
    % Its half is an integer, so the number is even.
    Peculiar #= 2 * Half,
    % If you add 1 to it the result is a square number.
    A * A #= Peculiar + 1,
    % If you add 1 to its half, you also get a square number.
    B * B #= Half + 1.
