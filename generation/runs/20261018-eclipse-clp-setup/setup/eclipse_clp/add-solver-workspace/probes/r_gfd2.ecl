:- lib(gfd).

p_or :- X :: 1..9, Y :: 1..9, (X #> 5) or (Y #> 3), Y #= 2, writeln(X).
p_and :- X :: 1..9, Y :: 1..9, (X #> 5) and (Y #> 3), writeln(X-Y).
p_neg :- X :: 1..9, neg (X #> 5), writeln(X).
p_b :- X :: 1..9, B #= (X #> 5), X #= 7, writeln(B).
p_eq :- X :: 1..9, B :: 0..1, B #= (X #> 5), X #= 7, writeln(B).
p_big :- X :: 0..2000000000, Y #= X * 2, writeln(Y).
p_big2 :- X :: 0..2000000000, Y #= X * 2, writeln(X-Y).
p_big3 :- X :: 0..1000000000, Y #= X * 2, writeln(X-Y).
p_alldistinct :- Xs = [_A,_B], Xs :: 1..3, alldifferent(Xs), writeln(ok).
