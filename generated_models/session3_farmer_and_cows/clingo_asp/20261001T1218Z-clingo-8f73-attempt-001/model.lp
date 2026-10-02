% Farmer and cows: a farmer shares his cows among his sons. Cow number c gives c units of milk.
% Every son gets the stated number of cows and all sons get the same total quantity of milk.
% Instance facts: num_cows(N); num_sons(K); cows_per_son(S,C): son S gets C cows.
cow(0..N-1) :- num_cows(N).
son(0..K-1) :- num_sons(K).

% The milk of cow I (counted from 0) is I+1, because the cows are numbered from 1 up to the total.
% The milk each son must get is the total milk divided by the number of sons (integer division,
% as in the reference, which only has solutions when it divides evenly).
total_milk(T) :- num_cows(N), T = N*(N+1)/2.
milk_per_son(M) :- total_milk(T), num_sons(K), M = T/K.

% cow_assignments(I,S): cow I goes to son S. Every cow goes to exactly one son.
1 { cow_assignments(I,S) : son(S) } 1 :- cow(I).

% Each son gets the specific number of cows.
:- cows_per_son(S,C), #count { I : cow_assignments(I,S) } != C.

% The total milk of the cows each son gets is the same: milk_per_son.
:- son(S), milk_per_son(M), #sum { I+1,I : cow_assignments(I,S) } != M.

#show cow_assignments/2.
