:- lib(ic).
:- lib(ic_global_gac).

p_gcc :- Xs = [_A,_B,_C], Xs :: 1..2, gcc([gcc(1,2,1), gcc(1,2,2)], Xs), labeling(Xs), writeln(Xs).
