% Curious number: 48 has the peculiarity that adding 1 to it gives a square and
% adding 1 to its half gives a square. Find another number, from 1 to 10000, with it.
% The puzzle is fixed by the problem; the instance carries no data.
% square(S): S is a square of at most 10000.
square(R*R) :- R = 1..100.

% peculiar(N): the number is N; N + 1 must be at most 10000.
1 { peculiar(N) : N = 1..9999 } 1.

% 48 is already known.
:- peculiar(48).
% If you add 1 to it the result is a square number.
:- peculiar(N), not square(N+1).
% Its half is a whole number c >= 1, and c + 1 is a square number.
:- peculiar(N), N \ 2 != 0.
:- peculiar(N), not square(N/2+1).

#show peculiar/1.
