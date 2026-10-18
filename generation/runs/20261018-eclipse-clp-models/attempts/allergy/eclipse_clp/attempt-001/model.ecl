% Allergy puzzle: four friends (Debra = 0, Janet = 1, Hugh = 2, Rick = 3) are each
% allergic to something different (eggs, mold, nuts, ragweed) and each has a
% different surname (Baxter, Lemon, Malone, Fleet). Each output is the index of
% the friend who has that surname or allergy.

:- lib(ic).

model(_Instance, Vars, Outputs) :-
    Vars = [Baxter, Eggs, Fleet, Lemon, Malone, Mold, Nuts, Ragweed],
    Vars :: 0..3,

    % each of them is allergic to something different
    % (eggs, mold, nuts and ragweed belong to different friends)
    alldifferent([Eggs, Mold, Nuts, Ragweed]),

    % each one's surname is different (Baxter, Lemon, Malone and Fleet)
    alldifferent([Baxter, Lemon, Malone, Fleet]),

    % Rick is not allergic to mold
    Mold #\= 3,

    % Baxter is allergic to eggs
    Baxter #= Eggs,

    % Hugh is neither surnamed Lemon nor Fleet
    Lemon #\= 2,
    Fleet #\= 2,

    % Debra is allergic to ragweed
    Ragweed #= 0,

    % Janet (who isn't Lemon) is neither allergic to eggs nor to mold
    Lemon #\= 1,
    Eggs #\= 1,
    Mold #\= 1,

    Outputs = [baxter-Baxter, eggs-Eggs, fleet-Fleet, lemon-Lemon,
               malone-Malone, mold-Mold, nuts-Nuts, ragweed-Ragweed].
