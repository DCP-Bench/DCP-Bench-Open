:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Template design: a printing firm makes several variations of a product from
% a few templates, each template carrying a fixed number of slots. Decide how
% many copies of each variation go on each template and how many sheets are
% printed from each template, so that every variation's demand is met with as
% few printed sheets as possible.
model(Instance, Vars, [production-Production, layout-Layout], min(Total)) :-
    NSlots = Instance.n_slots,              % slots on a template
    NTemplates = Instance.n_templates,
    NVar = Instance.n_var,                  % variations
    Demand = Instance.demand,               % Demand[v]: copies needed of variation v
    max_list(Demand, UpperBound),           % no template is printed more often than this

    % Production[t] is the number of sheets printed from template t, and
    % Layout[t][v] the number of slots of template t holding variation v.
    length(Production, NTemplates),
    Production ins 1..UpperBound,
    length(Layout, NTemplates),
    maplist({NVar}/[Row]>>(length(Row, NVar), Row ins 0..NVar), Layout),

    % all slots are populated in a template
    maplist({NSlots}/[Row]>>sum(Row, #=, NSlots), Layout),

    % meet demand: a sheet from template t carries Layout[t][v] copies of
    % variation v, so the copies printed of variation v add up to at least its
    % demand
    transpose(Layout, ByVariation),
    maplist({Production}/[Column, Needed]>>
                (maplist([Sheets, Slots, Copies]>>(Copies #= Sheets * Slots),
                         Production, Column, CopiesPerTemplate),
                 sum(CopiesPerTemplate, #>=, Needed)),
            ByVariation, Demand),

    % Implied: every template fills all its slots, so the sheets together carry
    % at least the total demand.
    sum_list(Demand, TotalDemand),
    sum(Production, #=, Total),
    NSlots * Total #>= TotalDemand,

    % the search decides the layouts first, then the sheets printed
    append(Layout, Cells),
    append(Cells, Production, Vars).
