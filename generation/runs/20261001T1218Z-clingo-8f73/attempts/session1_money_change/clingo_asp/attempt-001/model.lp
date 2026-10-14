% Money change: give Bob the stated amount using coins of several types, no more of a type than
% are available, with as few coins as possible.
% Instance facts: amount(A); types_of_coins(I,V): coin type I is worth V; available_coins(I,N): N coins of type I exist.
coin_type(I) :- types_of_coins(I,_).

% Coins given use an order encoding: given(I,K) holds when at least K coins of type I are given,
% K in 1..available (the reference allows 0..max available and also bounds each type by its own supply).
{ given(I,K) : K = 1..N } :- available_coins(I,N).
:- given(I,K+1), not given(I,K), K >= 1.

% coin_counts(I,K): exactly K coins of type I are given.
coin_counts(I,0) :- coin_type(I), not given(I,1).
coin_counts(I,K) :- given(I,K), not given(I,K+1).

% The coins given add up to the amount: each coin of type I contributes its value.
:- amount(A), #sum { V,I,K : given(I,K), types_of_coins(I,V) } != A.

% Minimise the number of coins given.
#minimize { 1,I,K : given(I,K) }.

#show coin_counts/2.
