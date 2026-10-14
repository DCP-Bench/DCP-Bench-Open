:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Aircraft landing with a fixed landing order: give every aircraft a landing
% time inside its window so that consecutive landings keep the required
% separation, minimising the penalty for landing before or after the target.
model(Instance, Vars, [landing_times-Times, total_penalty-Total], min(Total)) :-
    Earliest = Instance.earliest_landing,   % start of each aircraft's window
    Latest = Instance.latest_landing,       % end of each aircraft's window
    Target = Instance.target_landing,       % preferred landing time
    PenaltyBefore = Instance.penalty_before, % cost per time unit landing early
    PenaltyAfter = Instance.penalty_after,   % cost per time unit landing late
    Separation = Instance.separation_time,   % minimum gap between two landings
    length(Earliest, N),
    max_list(Latest, Horizon),

    length(Times, N), Times ins 0..Horizon,
    % how far before / after its target each aircraft lands
    length(Earlier, N), Earlier ins 0..Horizon,
    length(Later, N), Later ins 0..Horizon,

    % each aircraft lands inside its time window
    maplist([T, Lo, Hi]>>(T #>= Lo, T #=< Hi), Times, Earliest, Latest),

    % the deviation from the target is split into earliness and lateness; the
    % positive penalties make the solver keep one of the two at zero
    maplist([T, Goal, Late, Early]>>(T - Goal #= Late - Early), Times, Target, Later, Earlier),

    % the landing order is fixed as the aircraft index order (as the problem
    % states), so aircraft J lands at least Separation[I][J] after aircraft I
    findall(I-J, (between(1, N, I), I1 is I + 1, between(I1, N, J)), Pairs),
    maplist({Times, Separation}/[I-J]>>(nth1(I, Times, Ti), nth1(J, Times, Tj),
                                        nth1(I, Separation, Row), nth1(J, Row, Gap),
                                        Tj - Ti #>= Gap), Pairs),

    % total penalty for early and late landings
    append(PenaltyBefore, PenaltyAfter, Prices),
    append(Earlier, Later, Deviations),
    sum_list(Prices, PriceSum),
    Bound is Horizon * PriceSum,
    Total in 0..Bound,
    scalar_product(Prices, Deviations, #=, Total),
    append([Times, Earlier, Later, [Total]], Vars).
