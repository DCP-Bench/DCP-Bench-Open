% Coins: choose how many coins of each denomination to carry, as few as
% possible in total, so that every amount from 1 up to (but not including) the
% maximum can be paid exactly.
% denominations(I, D): coin I is worth D cents; max_amount_to_pay(M): amounts 1..M-1 must be payable.
coin(I) :- denominations(I,_).
amount(1..M-1) :- max_amount_to_pay(M).
% More than (M - 1) / D coins of value D can never be used to pay an amount below M.
most(I,(M - 1) / D) :- denominations(I,D), max_amount_to_pay(M).

% x(I, N): N coins of denomination I are carried.
1 { x(I,N) : N = 0..K } 1 :- most(I,K).

% pay(A, I, N): to pay amount A, N coins of denomination I are used.
1 { pay(A,I,N) : N = 0..K } 1 :- amount(A), most(I,K).

% A payment uses no more coins of a kind than are carried and adds up to the amount.
:- pay(A,I,N), x(I,C), N > C.
:- amount(A), A != #sum { D * N,I : pay(A,I,N), denominations(I,D) }.

% Carry as few coins as possible.
#minimize { N,I : x(I,N) }.

#show x/2.
