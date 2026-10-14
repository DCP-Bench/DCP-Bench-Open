% Pythagorean triplet: three natural numbers a, b, c with a^2 + b^2 = c^2 and a + b + c = 1000.
% The sum 1000 and the bound 500 on each number belong to the problem statement (there is no
% instance data).

number(1..500).

% a and b are chosen, each between 1 and 500.
1 { a(N) : number(N) } 1.
1 { b(N) : number(N) } 1.

% c is what is left of the sum 1000. It is derived instead of chosen: choosing all three and
% checking a + b + c = 1000 would ground 500^3 combinations.
c(1000 - A - B) :- a(A), b(B).
:- c(C), not number(C).

% a^2 + b^2 = c^2, with c written out as 1000 - a - b to keep the grounding at 500^2 rules.
:- a(A), b(B), A*A + B*B != (1000 - A - B) * (1000 - A - B).

#show a/1.
#show b/1.
#show c/1.
