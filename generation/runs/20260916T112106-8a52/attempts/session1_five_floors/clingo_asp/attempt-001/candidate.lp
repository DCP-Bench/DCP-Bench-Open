% Five floors: put Baker, Cooper, Fletcher, Miller and Smith on five different
% floors. The declared outputs are named with capitals, which the runner
% carries on the lowered predicate.
floor(1..5).

1 { b(F) : floor(F) } 1.
1 { c(F) : floor(F) } 1.
1 { f(F) : floor(F) } 1.
1 { m(F) : floor(F) } 1.
1 { s(F) : floor(F) } 1.

lives(baker,F) :- b(F).
lives(cooper,F) :- c(F).
lives(fletcher,F) :- f(F).
lives(miller,F) :- m(F).
lives(smith,F) :- s(F).
:- lives(X,F), lives(Y,F), X < Y.

:- b(5).
:- c(1).
:- f(5).
:- f(1).
:- m(M), c(C), M <= C.
:- s(S), f(F), |S - F| == 1.
:- f(F), c(C), |F - C| == 1.

#show b/1.
#show c/1.
#show f/1.
#show m/1.
#show s/1.
