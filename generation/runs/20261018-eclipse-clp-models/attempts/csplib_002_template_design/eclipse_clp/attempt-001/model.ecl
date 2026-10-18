% Template design (CSPLib 002): decide how many templates to produce, which
% variations and how many copies of each go on each template, and how many
% sheets to print from each template, so that every variation's demand is met
% and the total number of printed sheets is minimal.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [layout-Layout, production-Prod], Objective) :-
    memberchk(n_slots-S, Instance),
    memberchk(n_templates-T, Instance),
    memberchk(n_var-V, Instance),
    memberchk(demand-Demand, Instance),
    % the largest demand bounds the number of sheets printed from one template
    ( foreach(D, Demand), fromto(0, A, B, MaxD) do B is max(A, D) ),
    % a template holds several copies of each variation: layout[t][v] in 0..slots
    length(Layout, T),
    ( foreach(R1, Layout), param(V, S) do
        length(R1, V),
        R1 :: 0..S
    ),
    % sheets printed from each template
    length(Prod, T),
    Prod :: 0..MaxD,
    % each template carries at most n_slots variations (copies)
    ( foreach(R2, Layout), param(S) do
        sum(R2) #=< S
    ),
    % the demand for each variation must be met over all templates
    % (copies on template t times sheets printed from template t)
    ( for(J, 1, V), param(Layout, Prod, Demand) do
        nth1(J, Demand, Dj),
        ( foreach(R3, Layout), foreach(P, Prod), foreach(Term, Terms), param(J) do
            nth1(J, R3, C),
            Term #= C * P
        ),
        sum(Terms) #>= Dj
    ),
    flatten(Layout, FlatLayout),
    append(FlatLayout, Prod, Vars),
    Objective = min(sum(Prod)).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
