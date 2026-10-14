% Template design (CSPLib 2): a printing firm prints several variations of a
% carton from templates, each template holding n_slots slots that carry copies
% of the variations. Decide how many printed sheets each template is run for
% and how many copies of each variation each template carries, so that every
% variation's demand is met with as few printed sheets in total as possible.

int: n_slots;          % slots on a template
int: n_templates;      % number of different templates
int: n_var;            % number of variations
array[int] of int: demand;  % demand[v] = how many items of variation v are ordered

set of int: Templates = 1..n_templates;
set of int: Variations = 1..n_var;

% a template is never run for more sheets than the largest demand
int: ub = max(demand);

% production[t] = number of sheets printed from template t
array[Templates] of var 1..ub: production;

% layout[t, v] = number of copies of variation v on template t
% (the reference allows up to n_var copies of a variation on one template)
array[Templates, Variations] of var 0..n_var: layout;

% all slots are populated in a template
constraint forall(t in Templates) (sum(v in Variations) (layout[t, v]) = n_slots);

% the demand of every variation is met: each sheet of template t yields
% layout[t, v] items of variation v
constraint forall(v in Variations)
    (sum(t in Templates) (production[t] * layout[t, v]) >= demand[v]);

% Implied: every printed sheet carries n_slots items, so the sheets must be
% enough to cover the total demand
constraint n_slots * sum(production) >= sum(demand);

% minimise the total number of printed sheets
var int: objective = sum(production);
solve minimize objective;

output ["{\"production\": [", join(", ", [show(production[t]) | t in Templates]),
        "], \"layout\": [", join(", ", ["[" ++ join(", ", [show(layout[t, v]) | v in Variations]) ++ "]" | t in Templates]), "]}"];
