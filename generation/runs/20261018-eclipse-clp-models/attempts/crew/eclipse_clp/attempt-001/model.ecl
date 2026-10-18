% Crew assignment: assign 20 flight attendants to 10 flights.
% Each flight needs a certain number of cabin crew, and they have to speak
% certain languages. Every cabin crew member has two flights off after an
% attended flight. crew[f][p] is 1 if person p is assigned to flight f.

:- lib(ic).
:- lib(listut).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

model(Instance, Vars, [crew-Crew]) :-
    memberchk(attributes-Attr, Instance),
    memberchk(required_crew-Req, Instance),
    length(Attr, NP),
    length(Req, NF),
    length(Crew, NF),
    % crew[f][p] is 0 or 1
    ( foreach(Row, Crew), param(NP) do
        length(Row, NP),
        Row :: 0..1
    ),
    % Each flight needs a certain number of cabin crew (the total), and they
    % have to speak certain languages (at least the required number of
    % attendants per attribute: steward, hostess, French, Spanish, German).
    ( foreach(Row, Crew), foreach(RQ, Req), param(Attr) do
        RQ = [Total | Mins],
        sum(Row) #= Total,
        ( for(K, 0, 4), param(Row, Attr, Mins) do
            nth0(K, Mins, Min),
            ( foreach(R, Row), foreach(A, Attr), foreach(T, Terms), param(K) do
                nth0(K, A, V),
                T #= R * V
            ),
            sum(Terms) #>= Min
        )
    ),
    % Every cabin crew member has two flights off after an attended flight:
    % if p works flight f, then p does not work flight f+1 or f+2.
    ( for(F, 0, NF-1), param(Crew, NF, NP) do
        ( for(D, 1, 2), param(F, Crew, NF, NP) do
            G is F + D,
            ( G < NF ->
                nth0(F, Crew, R1),
                nth0(G, Crew, R2),
                ( for(P, 0, NP-1), param(R1, R2) do
                    nth0(P, R1, X),
                    nth0(P, R2, Y),
                    X + Y #=< 1
                )
            ;
                true
            )
        )
    ),
    flatten(Crew, Vars).
