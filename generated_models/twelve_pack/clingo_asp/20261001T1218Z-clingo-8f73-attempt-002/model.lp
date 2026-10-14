% Twelve-pack problem: buy packs of several sizes so that the number of items reaches the target
% and is as close to it as possible (the smallest total that is at least the target).
% Instance facts: target(T); packs(I,P): pack size I holds P items.
pack(I) :- packs(I,_).

% Bound on the total. Buying only the smallest pack, as many as needed, gives a total below
% target + smallest pack size, so the best total is below that too. Totals above it can never be
% best, and neither can any count that would lead to one, so they are left out of the search; this
% never removes a best answer. It also keeps every count within the reference's range 0..2*target.
limit(T + Q - 1) :- target(T), Q = #min { P : packs(_,P) }.

% counts(I,V): V packs of size I are bought.
1 { counts(I,V) : V = 0..L/P } 1 :- packs(I,P), limit(L).

% The items are counted pack size by pack size: partial(I,Z) says that the packs of sizes
% 0..I-1 hold Z items together. A single "#sum" for the total would not let the solver see
% that no total below the target is possible.
partial(0,0).
partial(I+1,Z+P*V) :- partial(I,Z), counts(I,V), packs(I,P), Z + P*V <= L, limit(L).
total(Z) :- partial(N,Z), N = #count { I : pack(I) }.
:- not total(_).

% The total must reach the target.
:- total(Z), target(T), Z < T.

% The total is to be as small as possible, so it is as close to the target as the pack sizes allow.
#minimize { Z : total(Z) }.

#show counts/2.
