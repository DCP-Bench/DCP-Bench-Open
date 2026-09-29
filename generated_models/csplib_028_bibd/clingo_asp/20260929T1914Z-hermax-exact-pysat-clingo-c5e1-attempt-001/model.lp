% Balanced incomplete block design: arrange v objects into b blocks so that a
% block holds k objects, an object lies in r blocks, and any two distinct
% objects share exactly l blocks. Solved through the v x b incidence matrix.
object(0..V-1) :- v(V).
block(0..B-1) :- b(B).

% in(I, J): object I belongs to block J; matrix/3 reports that as 1 or 0.
{ in(I,J) } :- object(I), block(J).
matrix(I,J,1) :- in(I,J).
matrix(I,J,0) :- object(I), block(J), not in(I,J).

% Every object occurs in exactly r blocks (each row adds up to r).
:- object(I), r(R), R != #count { J : in(I,J) }.
% Every block contains exactly k objects (each column adds up to k).
:- block(J), k(K), K != #count { I : in(I,J) }.
% Any two distinct objects occur together in exactly l blocks.
:- object(I1), object(I2), I1 < I2, l(L), L != #count { J : in(I1,J), in(I2,J) }.

#show matrix/3.
