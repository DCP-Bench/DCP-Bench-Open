% chess_set: a small joinery makes two sizes of boxwood chess sets each week.
% Decide how many small sets and large sets to make so as to maximize profit.
% Output: small_set, large_set, max_profit.

:- lib(ic).

model(_Instance, [Small, Large], [small_set-Small, large_set-Large, max_profit-Profit], max(Profit)) :-
    % Quantities are non-negative whole numbers of sets.
    Small :: 0..200,
    Large :: 0..200,

    % The small set requires 3 hours of machining on a lathe, and the large set requires 2 hours.
    % There are four lathes with skilled operators who each work a 40 hour week, so we have 160 lathe-hours per week.
    3 * Small + 2 * Large #=< 160,

    % The small chess set requires 1 kg of boxwood, and the large set requires 3 kg.
    % Boxwood is scarce and only 200 kg per week can be obtained.
    Small + 3 * Large #=< 200,

    % When sold, each of the large chess sets yields a profit of $20, and one of the small chess set has a profit of $5.
    % The problem is to decide how many sets of each kind should be made each week so as to maximize profit.
    Profit #= 5 * Small + 20 * Large.
