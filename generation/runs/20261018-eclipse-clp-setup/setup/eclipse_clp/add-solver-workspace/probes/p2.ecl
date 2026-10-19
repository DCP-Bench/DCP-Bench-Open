:- lib(ic).
:- lib(ic_global).
:- lib(listut).

tt(Name, G) :- ( catch(G, E, (printf("EXC %s: %w%n", [Name, E]), fail)) -> printf("ok   %s%n", [Name]) ; printf("FAIL %s%n", [Name]) ).

p2 :-
    [A,B,C] :: 1..3,
    tt("ordered <", ic_global:ordered(<, [A,B,C])),
    tt("ordered < 2", ic_global:ordered(<, [1,2,3])),
    tt("sorted", ic_global:sorted([A,B,C],[A,B,C])),
    tt("occurrences", ic_global:occurrences(1, [A,B,C], _)),
    tt("gcc", ic_global:gcc([A,B,C], [1-_,2-_,3-_])),
    tt("disjunctive", ic_global:disjunctive([task(A,1,_,_,_), task(B,1,_,_,_)])),
    tt("cumulative2", ic_global:cumulative([task(A,1,_,_,_)], [limit(2)])),
    tt("table ic", ic_global:table([[A,B]], [[1,2]])),
    tt("circuit", ic:circuit([A,B,C])),
    tt("alldistinct", ic_global:alldistinct([A,B,C])),
    tt("lex_le", ic:lex_le([A,B],[B,C])),
    tt("cumulative3", ic_global:cumulative([task(A,1,_,_,_)], [limit(2)])),
    printf("done p2%n", []).

:- p2, halt.
:- halt.
