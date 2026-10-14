% Broken weights: a weight of m pounds broke into n pieces of whole-pound
% weights. Find piece weights that let a balance scale weigh every whole weight
% from 1 to m, where a piece may go on the same pan as the object, on the other
% pan, or stay off the scale.

% weights(J, W): piece J weighs W pounds; the pieces together weigh m.
1 { weights(J,W) : W = 1..M } 1 :- n(N), m(M), J = 0..N-1.
:- m(M), M != #sum { W,J : weights(J,W) }.

% side(T, J, X): to weigh T pounds, piece J goes on the same pan as the object (1),
% on the other pan (-1) or stays off the scale (0).
1 { side(T,J,X) : X = -1..1 } 1 :- m(M), n(N), T = 1..M, J = 0..N-1.

% The signed weights add up to the weight being measured.
:- m(M), T = 1..M, T != #sum { W * X,J : weights(J,W), side(T,J,X) }.

#show weights/2.
