:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Allergy logic puzzle: match each friend to a surname and an allergy.
% Friends are numbered Debra 0, Janet 1, Hugh 2, Rick 3.
model(_Instance, Vars, [eggs-Eggs, mold-Mold, nuts-Nuts, ragweed-Ragweed,
                        baxter-Baxter, lemon-Lemon, malone-Malone, fleet-Fleet]) :-
    Foods = [Eggs, Mold, Nuts, Ragweed],
    Surnames = [Baxter, Lemon, Malone, Fleet],
    append(Foods, Surnames, Vars),
    Vars ins 0..3,
    all_distinct(Foods),
    all_distinct(Surnames),

    Mold #\= 3,        % Rick is not allergic to mold
    Eggs #= Baxter,
    Lemon #\= 2,       % Hugh is neither Lemon nor Fleet
    Fleet #\= 2,
    Ragweed #= 0,      % Debra is allergic to ragweed
    Lemon #\= 1,       % Janet is not Lemon, nor allergic to eggs or mold
    Eggs #\= 1,
    Mold #\= 1.
