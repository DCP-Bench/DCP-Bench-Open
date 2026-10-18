% Aircraft assignment: assign aircraft of several types to several routes.
% allocation[i][j] is the number of aircraft of type i assigned to route j.
% Each route must meet its passenger demand, each aircraft type is limited by
% its availability, and the total operational cost is minimised.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [allocation-Alloc], Objective) :-
    memberchk(availability-Avail, Instance),
    memberchk(demand-Demand, Instance),
    memberchk(capabilities-Cap, Instance),
    memberchk(costs-Costs, Instance),
    length(Avail, NT),
    length(Demand, NR),
    NR1 is NR - 1,
    % Allocation matrix: one row per aircraft type, one column per route.
    length(Alloc, NT),
    ( foreach(Row0, Alloc), param(NR) do length(Row0, NR) ),
    flatten(Alloc, Vars),
    % Each cell is bounded by the availability of its aircraft type.
    ( foreach(Row1, Alloc), foreach(A1, Avail) do Row1 :: 0..A1 ),

    % Each route has a specific passenger demand that must be satisfied.
    ( for(J, 0, NR1), param(Alloc, Cap, Demand) do
        nth0(J, Demand, D),
        ( foreach(Row2, Alloc), foreach(CRow, Cap), foreach(P, Seats), param(J) do
            nth0(J, Row2, X),
            nth0(J, CRow, C),
            P #= C * X
        ),
        sum(Seats) #>= D
    ),

    % Each aircraft type has a limited number of available units.
    ( foreach(Row3, Alloc), foreach(A3, Avail) do sum(Row3) #=< A3 ),

    % Minimise the total operational cost of the assignment.
    flatten(Costs, FlatCosts),
    ( foreach(X4, Vars), foreach(C4, FlatCosts), foreach(T, Terms) do T #= C4 * X4 ),
    Obj #= sum(Terms),
    Objective = min(Obj).
