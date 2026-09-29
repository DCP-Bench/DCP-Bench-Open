% Hadamard matrix (Legendre pairs): for an odd l with m = (l - 1) / 2, find two
% sequences a and b of length l with entries +1 or -1, each summing to 1, whose
% periodic autocorrelations satisfy PAF(a, s) + PAF(b, s) = -2 for s = 1..m.
index(0..L-1) :- l(L).
shift(1..(L-1)/2) :- l(L).
sign(-1;1).

% a(I, V), b(I, V): entry I of the sequence is V, either -1 or +1.
1 { a(I,V) : sign(V) } 1 :- index(I).
1 { b(I,V) : sign(V) } 1 :- index(I).

% Each sequence sums to 1.
:- #sum { V,I : a(I,V) } != 1.
:- #sum { V,I : b(I,V) } != 1.

% PAF(a, s) + PAF(b, s) = -2, with PAF(x, s) the sum over i of x_i * x_(i+s mod l).
:- shift(S), l(L),
   #sum { VA*VB,a,I : a(I,VA), a((I + S) \ L,VB) ; VA*VB,b,I : b(I,VA), b((I + S) \ L,VB) } != -2.

#show a/2.
#show b/2.
