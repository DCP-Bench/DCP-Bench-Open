slot(0..2*K-1) :- k(K).
val(1..K) :- k(K).

% Each value starts somewhere, and its second copy sits V+1 slots later.
1 { start(V,S) : slot(S) } 1 :- val(V).
:- k(K), start(V,S), S + V + 1 > 2*K - 1.

sol(S,V) :- start(V,S).
sol(S2,V) :- start(V,S), S2 = S + V + 1.

% Exactly one value per slot.
:- slot(S), #count { V : sol(S,V) } != 1.

#show sol/2.
