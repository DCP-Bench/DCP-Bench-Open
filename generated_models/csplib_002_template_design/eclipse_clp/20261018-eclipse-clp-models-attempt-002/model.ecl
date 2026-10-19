% Template design (CSPLib 002): a printing firm prints cartons from mother
% sheets. Each template is an aluminium sheet with several variations etched
% on it, and every printed sheet holds n_slots items. Decide how many copies
% of each variation go on each template (layout) and how many sheets to print
% from each template (production), so that the demand of every variation is
% met and the total number of printed sheets is minimal.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [layout-Layout, production-Prod], Objective) :-
    memberchk(n_slots-S, Instance),
    memberchk(n_templates-T, Instance),
    memberchk(n_var-V, Instance),
    memberchk(demand-Demand, Instance),
    % total demand and the largest single demand
    ( foreach(D, Demand), fromto(0, A, B, Dsum) do B is A + D ),
    ( foreach(D, Demand), fromto(0, A, B, MaxD) do B is max(A, D) ),

    % every template carries exactly n_slots copies, each variation 0..n_slots
    length(Layout, T),
    ( foreach(Row, Layout), param(V, S) do
        length(Row, V),
        Row :: 0..S,
        sum(Row) #= S
    ),

    % sheets printed from each template; no template needs more sheets than the
    % largest demand, since that already covers each variation it carries
    length(Prod, T),
    Prod :: 0..MaxD,
    Total #= sum(Prod),

    % Z[t][v] is the number of items of variation v printed from template t
    ( foreach(LRow, Layout), foreach(P, Prod), foreach(ZRow, Z),
      param(S, MaxD, V) do
        length(ZRow, V),
        ZRow :: 0..S*MaxD,
        ( foreach(L, LRow), foreach(Zc, ZRow), param(P) do
            Zc #= L * P
        ),
        % every printed sheet of a template holds n_slots items
        sum(ZRow) #= S * P
    ),

    % the items of each variation must cover its demand
    ( for(J, 1, V), param(Z, Demand, Dsum, S, Total) do
        nth1(J, Demand, Dj),
        ( foreach(ZRow, Z), foreach(Zj, Col), param(J) do
            nth1(J, ZRow, Zj)
        ),
        sum(Col) #>= Dj,
        % the other variations take at least their own demand, so this one
        % cannot take more than the total area minus theirs
        sum(Col) #=< S * Total - (Dsum - Dj)
    ),

    % the total number of items printed is S * Total and must cover all demand
    S * Total #>= Dsum,

    flatten(Layout, FlatLayout),
    append(FlatLayout, Prod, Vars),
    Objective = min(Total).

% layout cells first, then the sheet counts, in the order given
search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).
