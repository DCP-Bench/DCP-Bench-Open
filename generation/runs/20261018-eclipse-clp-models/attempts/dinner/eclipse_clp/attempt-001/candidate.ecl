% Dinner problem: how many grandparents, parents and children go to dinner.
% We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children.
% Grandparents cost $3 for dinner, parents $2 and children $0.50.
% There must be 20 total people at dinner and it must cost $20.
% Print the number of grandparents, parents and children going to dinner.

:- lib(ic).

model(_Instance, [G, P, C], [grandparents-G, parents-P, children-C], none) :-
    % We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children
    [G] :: 1..6,
    [P] :: 1..10,
    [C] :: 1..40,

    % There must be 20 total people at dinner
    G + P + C #= 20,

    % Grandparents cost $3 for dinner, parents $2 and children $0.50 (costs in cents)
    % and it must cost $20 (2000 cents)
    300 * G + 200 * P + 50 * C #= 2000.
