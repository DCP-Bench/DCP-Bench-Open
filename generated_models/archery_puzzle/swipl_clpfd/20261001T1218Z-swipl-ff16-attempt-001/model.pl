:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% Archery puzzle: an archer may shoot as many arrows as she likes at targets
% worth given scores. Choose how many arrows hit each target so that the total
% score is as close as possible to the target score.
model(Instance, Vars, [hits-Hits], min(Deviation)) :-
    Targets = Instance.targets,              % points scored by one hit on each target
    TargetScore = Instance.target_score,     % total the archer aims for

    % Hits[i] = number of arrows that hit target i; the reference allows at most
    % target_score hits per target
    length(Targets, N),
    length(Hits, N),
    Hits ins 0..TargetScore,

    % the score reached is the points of all hits added up
    MaxScore is TargetScore * 2,    % bound taken from the reference
    Score in 0..MaxScore,
    scalar_product(Targets, Hits, #=, Score),

    % the deviation is the distance between the score reached and the target
    % score; it is what the archer wants small
    Deviation in 0..MaxScore,
    Deviation #= abs(TargetScore - Score),
    append(Hits, [Score, Deviation], Vars).
