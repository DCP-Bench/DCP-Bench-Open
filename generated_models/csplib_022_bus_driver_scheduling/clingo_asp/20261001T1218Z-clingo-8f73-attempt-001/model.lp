% Bus driver scheduling: from a set of possible shifts, each covering some pieces of work (tasks),
% choose shifts so that every task is covered by exactly one chosen shift, using as few shifts as possible.
% Instance facts: num_work(W) tasks numbered 0..W-1, num_shifts(S) shifts numbered 0..S-1,
% shifts(I, K, T): the K-th task covered by shift I is T (the lists have different lengths).
task(0..W-1) :- num_work(W).
shift(0..S-1) :- num_shifts(S).
covers(I,T) :- shifts(I,_,T).

% chosen(I): shift I is selected.
{ chosen(I) : shift(I) }.

% Each task is covered by exactly one selected shift.
:- task(T), #count { I : chosen(I), covers(I,T) } != 1.

% Minimise the number of shifts used (every shift costs the same).
#minimize { 1,I : chosen(I) }.

% x(I, true/false): whether shift I is selected.
x(I,true) :- chosen(I).
x(I,false) :- shift(I), not chosen(I).

#show x/2.
