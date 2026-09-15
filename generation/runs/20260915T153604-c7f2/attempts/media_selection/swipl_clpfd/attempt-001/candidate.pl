:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Media selection: buy the cheapest set of advertising media that still
% reaches every target audience at least once.
model(Instance, Vars, [is_selected-Selected, min_total_cost-Cost], min(Cost)) :-
    Audiences = Instance.target_audiences,
    Media = Instance.advertising_media,
    Incidence = Instance.incidence_matrix,
    Costs = Instance.media_costs,
    length(Media, NumMedia),
    length(Audiences, NumAudiences),
    length(Incidence, NumAudiences),
    length(Selected, NumMedia),
    Selected ins 0..1,
    sum_list(Costs, CostTotal),
    Cost in 0..CostTotal,
    Vars = [Cost|Selected],
    % Every audience must be reached by at least one selected medium; the
    % incidence matrix has one row per audience.
    maplist({Selected}/[Row]>>scalar_product(Row, Selected, #>=, 1), Incidence),
    scalar_product(Costs, Selected, #=, Cost).
