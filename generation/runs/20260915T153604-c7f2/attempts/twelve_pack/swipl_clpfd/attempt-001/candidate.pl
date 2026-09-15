:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Twelve pack: buy whole packs to reach at least the target number of items,
% overshooting by as little as possible.
model(Instance, Vars, [counts-Counts], min(Total)) :-
    Target = Instance.target,
    Packs = Instance.packs,
    length(Packs, N),
    length(Counts, N),
    % Pack-count ceiling of 2 * target follows the reference's max_val.
    MaxVal is Target * 2,
    Counts ins 0..MaxVal,
    Ceiling is MaxVal * N,
    Total in 0..Ceiling,
    Vars = [Total|Counts],
    scalar_product(Packs, Counts, #=, Total),
    Total #>= Target.
