% Progressive party problem (CSPLib 013).
% A yacht club party over several half-hour periods. Some boats are designated hosts
% and stay where they are; the crews of the other (guest) boats visit host boats in
% each period. The total number of people aboard a boat, including the host crew and
% the guest crews, must not exceed its capacity. A guest boat cannot revisit a host,
% and guest crews cannot meet more than once. Minimise the number of host boats.
%
% Outputs: is_host[b] = 1 if boat b is a host; visits[p][b] = the host boat that boat b
% visits in period p (a host visits itself, so visits[p][h] = h). All indices are 0-based.
% element/3 is 1-based, so the 0-based visit V is passed as index V+1.

:- lib(ic).
:- lib(lists).
:- lib(listut).

model(Instance, Vars, Outputs, min(sum(IsHost))) :-
    memberchk(n_boats-N, Instance),
    memberchk(n_periods-P, Instance),
    memberchk(capacity-Cap, Instance),
    memberchk(crew_size-Crew, Instance),
    Nm1 is N - 1,
    Nm2 is N - 2,
    length(IsHost, N),
    IsHost :: 0..1,
    length(Visits, P),
    ( foreach(Row, Visits), param(N, Nm1) do
        length(Row, N),
        Row :: 0..Nm1
    ),

    % Each boat is a host or a guest. A host boat stays at its own place, so it visits
    % itself in every period. Every boat visits a host boat in each period.
    ( foreach(Row, Visits), param(IsHost, Nm1) do
        ( for(B, 0, Nm1), param(IsHost, Row, Nm1) do
            nth0(B, IsHost, H),
            nth0(B, Row, V),
            (H #= 1) => (V #= B),
            I #= V + 1,
            element(I, IsHost, 1)
        )
    ),

    % Flags for each period: Bs[p][g][h] = 1 when boat g is at host h in period p.
    ( foreach(Row, Visits), foreach(Bp, Bs), param(N) do
        visit_flags(Row, N, Bp)
    ),

    % The total number of people aboard a host, including the host crew and the guest
    % crews visiting it, must not exceed its capacity.
    ( foreach(Bp, Bs), param(IsHost, Cap, Crew, N) do
        capacity_period(Bp, IsHost, Cap, Crew, N)
    ),

    % A guest boat cannot revisit a host: each guest visits each other boat at most once.
    % Host boats visit themselves every period, so their own pairs are skipped.
    ( for(G, 0, Nm1), param(Bs, Nm1) do
        ( for(H, 0, Nm1), param(Bs, G, Nm1) do
            ( G =:= H ->
                true
            ;   flag_list(Bs, G, H, Xs),
                sum(Xs) #=< 1
            )
        )
    ),

    % Guest crews cannot meet more than once: two boats share a host in at most one
    % period. The constraint is posted for all pairs; pairs with a host are implied by
    % the revisit rule above, and two hosts never share a place.
    ( for(G1, 0, Nm2), param(Visits, Nm1, Nm2) do
        G1p is G1 + 1,
        ( for(G2, G1p, Nm1), param(Visits, G1, Nm1) do
            ( foreach(Row, Visits), foreach(M, Ms), param(G1, G2) do
                nth0(G1, Row, V1),
                nth0(G2, Row, V2),
                M :: 0..1,
                M #= (V1 #= V2)
            ),
            sum(Ms) #=< 1
        )
    ),

    flatten(Visits, FlatVisits),
    append(IsHost, FlatVisits, Vars),
    Outputs = [is_host-IsHost, visits-Visits].

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% Visit flags for one period: Bp[g][h] = 1 when boat g visits host h.
visit_flags(Row, N, Bp) :-
    Nm1 is N - 1,
    ( for(G, 0, Nm1), foreach(BG, Bp), param(Row, Nm1) do
        ( for(H, 0, Nm1), foreach(X, BG), param(Row, G, Nm1) do
            nth0(G, Row, V),
            X :: 0..1,
            X #= (V #= H)
        )
    ).

% Capacity of each boat in one period: the host crew (when the boat is a host) plus the
% crews of the guest boats visiting it must not exceed its capacity.
capacity_period(Bp, IsHost, Cap, Crew, N) :-
    Nm1 is N - 1,
    sum(Crew, Tot),
    ( for(H, 0, Nm1), param(Bp, IsHost, Cap, Crew, Nm1, Tot) do
        nth0(H, IsHost, IH),
        nth0(H, Cap, CH),
        nth0(H, Crew, CrH),
        S0 #= CrH*IH,
        ( for(G, 0, Nm1), fromto(S0, In, Out, Load), param(Bp, H, Crew, Nm1, Tot) do
            Out :: 0..Tot,
            ( G =:= H ->
                Out #= In
            ;   nth0(G, Bp, BG),
                nth0(H, BG, X),
                nth0(G, Crew, CG),
                Out #= In + CG*X
            )
        ),
        Load #=< CH
    ).

% The flags of guest G against host H, one per period.
flag_list(Bs, G, H, Xs) :-
    ( foreach(Bp, Bs), foreach(X, Xs), param(G, H) do
        nth0(G, Bp, BG),
        nth0(H, BG, X)
    ).
