% De Bruijn sequence B(base, n): a cyclic sequence over an alphabet of `base`
% symbols, of length base**n, in which every string of n symbols occurs exactly
% once. Modelled as a cycle through all base**n windows of n consecutive symbols.
window(0..B**N-1) :- base(B), n(N).
place(0..N-1) :- n(N).
symbol(0..B-1) :- base(B).

% symbol_at(I, J, V): the J-th symbol (most significant first) of the window
% starting at position I is V.
1 { symbol_at(I,J,V) : symbol(V) } 1 :- window(I), place(J).

% number(I, X): the number (in the given base) read from window I.
number(I,X) :- window(I), base(B), n(N), X = #sum { V * B ** (N - 1 - J),J : symbol_at(I,J,V) }.

% Every possible string occurs exactly once, i.e. all window numbers differ.
:- number(I1,X), number(I2,X), I1 < I2.

% Consecutive windows overlap: window I shifted by one symbol is window I-1 ...
:- window(I), I >= 1, place(J), J >= 1, symbol_at(I-1,J,V), not symbol_at(I,J-1,V).
% ... and the last window continues into the first one, closing the cycle.
:- base(B), n(N), place(J), J >= 1, symbol_at(B**N-1,J,V), not symbol_at(0,J-1,V).

% The sequence is the first symbol of every window.
de_bruijn(I,V) :- symbol_at(I,0,V).

#show de_bruijn/2.
