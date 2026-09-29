% Clock triplets: arrange the numbers 1 to 12 on a clock face so that no three
% neighbouring numbers add up to more than 21.
% The puzzle is fixed by the problem; the instance carries no data.
% x(I, V): position I of the clock, 0 to 11, holds the number V.
1 { x(I,V) : V = 1..12 } 1 :- I = 0..11.

% Every number appears once.
:- x(I,V), x(J,V), I < J.

% triple(I, K): position K belongs to the three neighbouring positions starting at I
% (going round the clock).
triple(I,(I;(I+1)\12;(I+2)\12)) :- I = 0..11.
% No three neighbouring positions add up to more than 21.
:- I = 0..11, #sum { V,K : triple(I,K), x(K,V) } > 21.

#show x/2.
