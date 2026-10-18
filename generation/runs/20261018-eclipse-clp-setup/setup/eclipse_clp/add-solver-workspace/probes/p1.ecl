:- lib(ic).
:- lib(ic_global).
:- lib(listut).

t(G) :- ( catch(G, E, (printf("EXC %w~n", [E]), fail)) -> printf("ok   %w~n", [G]) ; printf("FAIL %w~n", [G]) ).

p1 :-
    printf("== ic globals~n", []),
    X1 = [A,B,C], A :: 1..3, B :: 1..3, C :: 1..3,
    t(alldifferent(X1)),
    t(alldistinct(X1)),
    t(ic_global:alldifferent(X1)),
    t(ic_global:sorted([A,B,C], [A,B,C])),
    t(ic_global:ordered(A, [B,C])),
    t(lex_le([A,B],[B,C])),
    t(nth0(0,[1,2],_)),
    t(nth1(1,[1,2],_)),
    t(element(1, [A,B,C], 2)),
    t(atmost(1, [A,B,C], 2)),
    t(occurrences(1, [A,B,C], 0)),
    t(gcc([A,B,C], [1-0,2-0,3-0])),
    t(disjunctive([]) ),
    t(circuit([])),
    t(table([[A,B]], [[1,2]])),
    printf("== ic: lib exports check~n", []).

:- p1, halt.
:- printf("done~n", []), halt.
