:- lib(ic).
main :- S=[2,1,3], S :: 1..3, ( circuit(S) -> writeln(selfloop_ok) ; writeln(selfloop_fail) ), T=[2,3,1], ( circuit(T) -> writeln(cyc_ok) ; writeln(cyc_fail) ), U=[1,3,2], U :: 1..3, ( circuit(U) -> writeln(u_ok) ; writeln(u_fail) ), halt.
