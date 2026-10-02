% Twelve-pack problem: buy packs of several sizes so that the number of items reaches the target
% and is as close to it as possible (the smallest total that is at least the target).
% Instance facts: target(T); packs(I,P): pack size I holds P items.
pack(I) :- packs(I,_).

% Packs bought use an order encoding: bought(I,V) holds when at least V packs of size I are bought.
% V ranges over 1..2*target, because the reference limits every count to 0..2*target.
{ bought(I,V) : V = 1..2*T } :- pack(I), target(T).
:- bought(I,V+1), not bought(I,V), V >= 1.

% counts(I,V): exactly V packs of size I are bought.
counts(I,0) :- pack(I), not bought(I,1).
counts(I,V) :- bought(I,V), not bought(I,V+1).

% The total number of items is the sum, over packs bought, of their sizes. It must reach the target.
:- target(T), #sum { P,I,V : bought(I,V), packs(I,P) } < T.

% The total is to be as small as possible, so it is as close to the target as the pack sizes allow.
#minimize { P,I,V : bought(I,V), packs(I,P) }.

#show counts/2.
