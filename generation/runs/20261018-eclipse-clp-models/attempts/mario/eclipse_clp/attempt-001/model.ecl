% Mario: collect as much gold as possible on a route that starts at Mario's
% house and ends at Luigi's house, without exceeding the fuel limit.
% The output s lists the house that succeeds each house; a house that is not
% on the route is its own successor.

:- lib(ic).
:- lib(listut).

model(Instance, S, [s-Out], max(Total)) :-
    memberchk(nHouses-N, Instance),
    memberchk(marioHouse-M0, Instance),
    memberchk(luigiHouse-L0, Instance),
    memberchk(fuelLimit-Limit, Instance),
    memberchk(arc_fuel-Arc, Instance),
    memberchk(goldInHouse-Gold, Instance),
    M is M0 + 1,
    L is L0 + 1,
    length(S, N),
    length(Out, N),
    length(Vis, N),
    length(Fuel, N),
    S :: 1..N,
    Vis :: 0..1,

    % The route from Mario's house back to Mario's house is one cycle over the
    % visited houses; houses not on the route point to themselves.
    circuit(S),

    % Mario starts at Mario's house, so Mario's house is on the route.
    nth1(M, S, SM),
    SM #\= M,

    % Luigi ends at Luigi's house, and the succeeding house of Luigi's house is
    % Mario's house.
    nth1(L, S, SL),
    SL #= M,

    % A house is visited exactly when it does not point to itself.
    ( for(I, 1, N), foreach(Sa, S), foreach(Va, Vis) do
          Va #= (Sa #\= I)
    ),

    % The fuel of each leg is the entry of the arc fuel matrix for that leg.
    ( foreach(Sb, S), foreach(Fb, Fuel), foreach(Row, Arc) do
          element(Sb, Row, Fb)
    ),

    % The fuel used on the route must not exceed the fuel limit.
    sum(Fuel) #=< Limit,

    % Mario collects the gold of every house he visits.
    ( foreach(G, Gold), foreach(Vb, Vis), foreach(T, Terms) do
          T #= G * Vb
    ),
    Total #= sum(Terms),

    % The output s[i] is the 0-based house that succeeds house i.
    ( foreach(Sc, S), foreach(Oc, Out) do
          Oc #= Sc - 1
    ).
