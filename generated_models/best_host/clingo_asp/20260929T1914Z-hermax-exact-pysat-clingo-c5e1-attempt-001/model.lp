% Best host: seat six guests round a table so that everyone sits only next to
% guests they get along with.
% The puzzle is fixed by the problem; the instance carries no data.
% Guests: 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
% likes(A, B): A is willing to sit next to B.
likes(0,3). likes(0,5).
likes(1,2). likes(1,4).
likes(2,1). likes(2,5).
likes(3,0). likes(3,4).
likes(4,1). likes(4,3).
likes(5,0). likes(5,2).

% x(I, G): guest G has seat I, going round the table.
1 { x(I,G) : G = 0..5 } 1 :- I = 0..5.

% Every guest gets one seat.
:- x(I,G), x(J,G), I < J.

% Two guests in neighbouring seats must each be willing to sit next to the other.
:- x(I,A), x(J,B), J = (I+1) \ 6, not likes(A,B).
:- x(I,A), x(J,B), J = (I+1) \ 6, not likes(B,A).

#show x/2.
