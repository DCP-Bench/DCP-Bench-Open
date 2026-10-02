% Curious set of integers (Martin Gardner): 1, 3, 8 and 120 form a set in which the product of any
% two members is one less than a perfect square. Find one more number, at least 0, that can be
% added to the set without destroying this property.
% Instance: n is the size of the set including the new number, max_val the largest allowed value.

% The first four members of the set are given by the problem statement.
given(0,1). given(1,3). given(2,8). given(3,120).

% x(I,V): member I of the set is V. Members 0..3 are the given ones, the others are chosen
% between 0 and max_val; the new number is the last member.
slot(0..N-1) :- n(N).
value(0..M) :- max_val(M).
has_given(I) :- given(I,_).
x(I,V) :- given(I,V), slot(I).
1 { x(I,V) : value(V) } 1 :- slot(I), not has_given(I).

% All members are different.
:- x(I,V), x(J,V), I < J.

% The product of any two members plus one is a perfect square p*p, with p at most max_val
% (the bound on the square root that the problem puts on every product).
square(P*P) :- value(P).
:- x(I,V), x(J,W), I < J, not square(V*W + 1).

number(V) :- n(N), x(N-1,V).

#show number/1.
