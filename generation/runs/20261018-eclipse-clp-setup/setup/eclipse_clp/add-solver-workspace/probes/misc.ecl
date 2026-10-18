:- lib(ic).

p_multi :- ( multifor([I,J], 1, [2,3]) do write(I-J), write(' ') ), nl.
p_real :- X $= 3 / 2, writeln(X).
p_real2 :- X :: 0.0..10.0, X * 2 $= 7, writeln(X).
