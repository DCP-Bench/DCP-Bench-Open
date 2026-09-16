% Five self-referential statements, the i-th claiming that exactly i of them
% are false.
idx(0..4).
truth(0..1).

1 { statements(I,V) : truth(V) } 1 :- idx(I).

false_count(K) :- K = #count { I : statements(I,0) }.

% Statement I is true exactly when the false count is I + 1.
:- statements(I,1), false_count(K), K != I + 1.
:- statements(I,0), false_count(K), K == I + 1.

#show statements/2.
