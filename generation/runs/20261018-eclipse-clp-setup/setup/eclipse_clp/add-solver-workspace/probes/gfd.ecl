:- lib(gfd).
:- lib(branch_and_bound).
:- lib(timeout).

p_gfd32 :- X :: 0..3000000000, writeln(X).
p_gfd32b :- X #:: 0..3000000000, writeln(X).
p_gfdmid :- Xs = [A,B], Xs :: 1..5, A #< B, search(Xs, 0, input_order, indomain_middle, complete, []), writeln(Xs).
p_gcc :- Xs = [A,B,C], Xs :: 1..2, gcc([gcc{low:1,high:2,value:1}, gcc{low:1,high:2,value:2}], Xs), labeling(Xs), writeln([A,B,C]).
p_table :- Xs = [A,_B], Xs :: 1..3, table(Xs, [[1,2],[2,3],[3,1]]), A #> 1, labeling(Xs), writeln(Xs).
p_cum :- Ss = [A,_B], Ss :: 0..5, cumulative(Ss, [2,2], [1,1], 1), A #= 0, labeling(Ss), writeln(Ss).
p_disj :- Ss = [A,_B], Ss :: 0..5, disjunctive(Ss, [2,2]), A #= 0, labeling(Ss), writeln(Ss).
p_circ :- Ss = [_A,_B,_C], Ss :: 1..3, circuit(Ss), labeling(Ss), writeln(Ss).
p_gfdvb :- X :: 1..9, X #> 3, get_var_bounds(X, L, H), writeln(L-H).
p_gfdvb2 :- X :: 1..9, X #> 3, get_bounds(X, L, H), writeln(L-H).
p_gfd_reif :- X :: 1..9, B :: 0..1, B #<=> (X #> 5), X #= 7, writeln(B).
p_gfd_reif2 :- X :: 1..9, B :: 0..1, B <=> (X #> 5), X #= 7, writeln(B).
p_gfd_alld :- Xs = [_A,_B], Xs :: 1..3, alldifferent(Xs), writeln(ok).
p_gfd_nolabel :- X :: 1..9, Y #= X * 2, writeln(Y).
p_timeout_gfd :- length(L, 100), L :: 1..100, ( fromto(L,[Q|R],R,[]) do ( foreach(Q2,R), count(D,1,_), param(Q) do Q #\= Q2, Q #\= Q2+D, Q #\= Q2-D ) ), timeout(search(L, 0, input_order, indomain_min, complete, []), 2, writeln(timed_out)).
