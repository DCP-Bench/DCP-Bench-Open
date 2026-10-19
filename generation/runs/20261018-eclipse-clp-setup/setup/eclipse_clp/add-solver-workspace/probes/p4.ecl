:- lib(ic).
:- lib(ic_global).
:- lib(listut).

tt(Name, G) :- ( catch(G, E, (printf("EXC %s: %w%n", [Name, E]), fail)) -> printf("ok   %s%n", [Name]) ; printf("FAIL %s%n", [Name]) ).

p4 :-
    [A,B,C] :: 1..3,
    tt("ic:cumulative/2", ic:cumulative([task(A,1,_,1,_)], [limit(2)])),
    tt("ic:cumulative/4", ic:cumulative([A],[1],[1],2)),
    tt("ic:disjunctive/1", ic:disjunctive([task(A,1,_,_,_), task(B,1,_,_,_)])),
    tt("ic_global:disjunctive", ic_global:disjunctive([A,B])),
    tt("ic:serialized/2", ic:serialized([A,B],[1,1])),
    tt("ic_global:cumulative/4", ic_global:cumulative([A],[1],[1],2)),
    tt("ic_global:cumulative/2", ic_global:cumulative([task(A,1,_,1,_)], [limit(2)])),
    tt("ic:tuples_in", ic:tuples_in([[A,B]], [[1,2]])),
    tt("ic:lex_le", ic:lex_le([A,B],[B,C])),
    tt("lex_le unqualified", lex_le([A,B],[B,C])),
    tt("ic:alldistinct", ic:alldistinct([A,B,C])),
    tt("ic_global:gcc", ic_global:gcc([A,B,C], [1-0])),
    tt("ic_global:table", ic_global:table([[A,B]], [[1,2]])),
    tt("ic_global:atmost", atmost(1,[A,B,C],2)),
    tt("ic:element", element(A,[1,2,3],_)),
    tt("ic:circuit", circuit([A,B,C])),
    tt("ic:sum", sum([A,B,C]) #= 6),
    tt("ic:dim", dim(_,[2,2])),
    tt("ic:multifor", multifor([I,J],1,2) ),
    printf("done p4%n", []).

:- p4, halt.
:- halt.
