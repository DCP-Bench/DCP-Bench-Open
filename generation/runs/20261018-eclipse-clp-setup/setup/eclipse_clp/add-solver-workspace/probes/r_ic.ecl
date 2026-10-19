:- lib(ic).

p_imp :- X :: 1..9, Y :: 1..9, (X #> 5) => (Y #> 3), X #= 7, writeln(Y).
p_iff :- X :: 1..9, B :: 0..1, B => (X #> 5), X #= 7, writeln(B).
p_iff2 :- X :: 1..9, Y :: 1..9, (X #> 5) <=> (Y #> 3), Y #= 2, writeln(X).
p_or :- X :: 1..9, Y :: 1..9, (X #> 5) or (Y #> 3), Y #= 2, writeln(X).
p_and :- X :: 1..9, Y :: 1..9, (X #> 5) and (Y #> 3), writeln(X-Y).
p_neg :- X :: 1..9, neg (X #> 5), writeln(X).
p_sum :- Xs = [A,B,C], Xs :: 1..3, sum(Xs) #= 9, writeln(Xs), writeln(A-B-C).
