% Mario: collect as much gold as possible on a route that starts at Mario's
% house and ends at Luigi's house, without exceeding the fuel limit.
% The output s lists the house that succeeds each house; a house that is not
% on the route is its own successor.
%
% ECLiPSe circuit/1 needs one cycle over all houses, so it cannot skip houses.
% The route is instead modelled with alldifferent on the successors (a house
% that is skipped points to itself) and an order on the route (Mario's house
% has position 1, and each successor on the route has the next position),
% which rules out cycles that do not pass through Mario's house.

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
    length(P, N),
    length(PS, N),
    S :: 1..N,
    Vis :: 0..1,
    P :: 1..N,

    % Each house is the successor of at most one house, so the successors
    % are all different.
    alldifferent(S),

    % Mario starts at Mario's house, so Mario's house is on the route and
    % has position 1 on the route.
    nth1(M, S, SM),
    SM #\= M,
    nth1(M, P, 1),

    % Luigi ends at Luigi's house, and the succeeding house of Luigi's house
    % is Mario's house.
    nth1(L, S, SL),
    SL #= M,

    % Each step along the route, except the step back to Mario's house, goes
    % to the next position on the route.
    ( foreach(Sb, S), foreach(PSb, PS), param(P) do
          element(Sb, P, PSb)
    ),
    ( for(I, 1, N), param(M), foreach(Sa, S), foreach(Pa, P), foreach(PSa, PS) do
          ( (Sa #\= I) and (Sa #\= M) ) => (PSa #= Pa + 1)
    ),

    % A house is visited exactly when it does not point to itself.
    ( for(I2, 1, N), foreach(Sc, S), foreach(Vc, Vis) do
          Vc #= (Sc #\= I2)
    ),

    % The fuel of each leg is the entry of the arc fuel matrix for that leg.
    ( foreach(Sd, S), foreach(Fd, Fuel), foreach(Row, Arc) do
          element(Sd, Row, Fd)
    ),

    % The fuel used on the route must not exceed the fuel limit.
    sum(Fuel) #=< Limit,

    % Mario collects the gold of every house he visits.
    ( foreach(G, Gold), foreach(Ve, Vis), foreach(T, Terms) do
          T #= G * Ve
    ),
    Total #= sum(Terms),

    % The output s[i] is the 0-based house that succeeds house i.
    ( foreach(Sf, S), foreach(Of, Out) do
          Of #= Sf - 1
    ).
