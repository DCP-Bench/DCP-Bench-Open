include "globals.mzn";

% Input data
int: n_slots = 9;          % Number of slots on a template
int: n_templates = 2;      % Number of templates
int: n_var = 7;            % Number of different variations
array[1..n_var] of int: demand = [250, 255, 260, 500, 500, 800, 1100]; % Demand per variation

% Decision variables
% layout[t,v] = number of copies of variation v on template t (0 if not included)
array[1..n_templates, 1..n_var] of var 0..n_slots: layout;

% production[t] = number of printed sheets for template t
array[1..n_templates] of var 0..max(demand): production;

% Constraints

% Each template can have at most n_slots copies in total
constraint
  forall(t in 1..n_templates) (
    sum(v in 1..n_var)(layout[t,v]) <= n_slots
  );

% The total production for each variation must meet or exceed demand
% total copies produced for variation v = sum over templates of (layout[t,v] * production[t])
constraint
  forall(v in 1..n_var) (
    sum(t in 1..n_templates)(layout[t,v] * production[t]) >= demand[v]
  );

% Solve: minimize total production (sum of all printed sheets)
var int: total_production = sum(t in 1..n_templates)(production[t]);
solve minimize total_production;

% Output in JSON format
output [
  "{",
  "\"production\": ", show(production), ",",
  "\"layout\": [",
    join(",",
      [ "[" ++ join(",", [show(layout[t,v]) | v in 1..n_var]) ++ "]" | t in 1..n_templates ]
    ),
  "]",
  "}"
];