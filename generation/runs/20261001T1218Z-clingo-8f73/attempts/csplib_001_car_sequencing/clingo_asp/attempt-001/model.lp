% Car sequencing: put the cars on the assembly line in an order such that every option
% station copes with its load, i.e. among any per_slots(O) consecutive cars at most
% at_most(O) need option O, while each car type is produced as often as demanded.
% Instance facts: demand(T, D): D cars of type T are to be built; requires(T, O, B): B is 1
% when type T needs option O; at_most(O, A) and per_slots(O, P): option O may be needed by
% at most A cars in any P consecutive slots.
type(T) :- demand(T,_).
option(O) :- at_most(O,_).

% The number of cars is the sum of the demands; the slots are numbered from 0.
cars(N) :- N = #sum { D,T : demand(T,D) }.
slot(0..N-1) :- cars(N).

% sequence(S, T): the car in slot S is of type T. Every slot holds exactly one car.
1 { sequence(S,T) : type(T) } 1 :- slot(S).

% The number of cars of each type in the sequence equals the demand for that type.
:- demand(T,D), D != #count { S : sequence(S,T) }.

% needs(S, O): the car in slot S needs option O, read from the requires table of its type.
needs(S,O) :- sequence(S,T), requires(T,O,1).

% A station must not be overloaded: in every window of per_slots(O) consecutive slots that
% fits on the line, at most at_most(O) cars need option O.
:- at_most(O,A), per_slots(O,P), cars(N), slot(S), S + P <= N,
   A < #count { S2 : needs(S2,O), S2 >= S, S2 < S + P }.

#show sequence/2.
