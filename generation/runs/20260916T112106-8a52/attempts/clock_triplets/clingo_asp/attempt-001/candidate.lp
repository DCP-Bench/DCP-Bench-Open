% Clock triplets: rearrange 1..12 around a clock face so that no three adjacent
% numbers sum above 21.
pos(0..11).
num(1..12).

1 { x(I,V) : num(V) } 1 :- pos(I).
:- x(I,V), x(J,V), I < J.

% Triplets wrap around the face.
:- x(I,A), x(J,B), x(K,C), pos(I), J == (I + 11) \ 12, K == (I + 10) \ 12,
   A + B + C > 21.

#show x/2.
