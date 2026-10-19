:- lib(ic).
:- lib(ic_global).

p_ambig :- alldifferent([_X,_Y]), writeln(ok).
p_gcc_ic :- Xs = [_A,_B,_C], Xs :: 1..2, gcc([gcc(1,2,1), gcc(1,2,2)], Xs), writeln(Xs).
p_gcc_ic2 :- Xs = [_A,_B,_C], Xs :: 1..2, gcc([gcc(1,2,1), gcc(1,2,2)], Xs), labeling(Xs), writeln(Xs).
p_occ :- Xs = [_A,_B,_C], Xs :: 1..2, occurrences(1, Xs, 2), labeling(Xs), writeln(Xs).
p_atmost :- Xs = [_A,_B,_C], Xs :: 1..2, atmost(1, Xs, 1), labeling(Xs), writeln(Xs).
