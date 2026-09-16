% Initials queue: ten mathematicians whose initials are ordered pairs from
% A..E, all distinct, with no letter shared with the person in front.
% Letters are encoded A=0 through E=4.
letter(0..4).
spot(0..9).
slot(0..1).

1 { queue(I,S,L) : letter(L) } 1 :- spot(I), slot(S).

% Each person's initials are two distinct letters in alphabetical order.
:- queue(I,0,X), queue(I,1,Y), X >= Y.
% No two people share both initials.
:- queue(I,0,X), queue(I,1,Y), queue(J,0,X), queue(J,1,Y), I < J.
% Nobody shares a letter with the person in front.
:- queue(I,_,L), queue(J,_,L), J == I + 1.

% BE at the front, CD behind, BD at the back.
:- not queue(0,0,1).
:- not queue(0,1,4).
:- not queue(1,0,2).
:- not queue(1,1,3).
:- not queue(9,0,1).
:- not queue(9,1,3).

#show queue/3.
