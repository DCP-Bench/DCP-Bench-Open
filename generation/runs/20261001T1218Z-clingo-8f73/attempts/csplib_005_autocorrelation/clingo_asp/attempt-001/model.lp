% Low autocorrelation binary sequences: build a sequence of n bits, each +1 or -1, that
% minimises the energy, the sum over all shifts k = 1..n-1 of the squared periodic
% autocorrelation C_k, where C_k is the sum over i of S_i * S_((i + k) mod n).
% Instance facts: n(N): the length of the sequence.
index(0..N-1) :- n(N).
shift(1..N-1) :- n(N).

% sequence(I, V): bit I of the sequence is V, which is +1 or -1.
{ positive(I) } :- index(I).
sequence(I,1) :- positive(I).
sequence(I,-1) :- index(I), not positive(I).

% product(K, I, P): the product S_i * S_((i + k) mod n) is P: +1 if the two bits are equal,
% otherwise -1. The index wraps around, which makes the autocorrelation periodic.
product(K,I,1) :- shift(K), n(N), sequence(I,V), sequence((I + K) \ N,V).
product(K,I,-1) :- shift(K), index(I), not product(K,I,1).

% paf(K, C): the periodic autocorrelation at shift K is C, the sum of the products.
paf(K,C) :- shift(K), C = #sum { P,I : product(K,I,P) }.

% The energy is the sum of the squares of all autocorrelations; it is to be minimised.
#minimize { C * C,K : paf(K,C) }.

#show sequence/2.
