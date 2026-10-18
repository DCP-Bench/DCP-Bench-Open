% Media selection: choose which advertising media to buy so that every
% target audience is reached, at minimum total campaign cost.
% Each audience (row of incidence_matrix) must be reached by at least one
% selected medium (column). Covering more than once is allowed.

:- lib(ic).

model(Instance, Sel, [is_selected-Sel, min_total_cost-Total], min(Total)) :-
    memberchk(media_costs-Costs, Instance),
    memberchk(incidence_matrix-Matrix, Instance),
    length(Costs, M),
    length(Sel, M),
    Sel :: 0..1,

    % every target audience is reached by at least one selected media
    ( foreach(Row, Matrix), param(Sel) do
        ( foreach(R, Row), foreach(S, Sel), foreach(R*S, Terms) do true ),
        sum(Terms) #>= 1
    ),

    % the total campaign cost is the sum of the costs of the selected media
    ( foreach(C, Costs), foreach(S, Sel), foreach(C*S, CostTerms) do true ),
    Total #= sum(CostTerms).
