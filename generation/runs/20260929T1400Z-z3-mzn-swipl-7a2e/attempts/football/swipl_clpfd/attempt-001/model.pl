:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Football squad: buy players for as close to GBP 30 million as possible without
% going over, taking the required number from each position and at least eleven
% players in total. The output is the total price in GBP thousands.
%
% The players on offer are fixed by the problem, so their prices (in GBP
% thousands) are mirrored here: position(Fewest, Most, Prices), where Most is the
% number of players on offer when the problem sets no upper limit.
budget(30000).
position(1, 1, [730, 1280, 3880]).                                                   % goalkeepers: exactly 1
position(2, 8, [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]).                     % defenders: 2 or more
position(3, 10, [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]).       % midfielders: 3 or more
position(2, 5, [4460, 6470, 7780, 8390, 9500]).                                      % strikers: 2 or more
min_players(11).  % at least this many players in all

model(_Instance, [Z|Bought], [z-Z], max(Z)) :-
    budget(Budget),
    min_players(MinPlayers),
    findall(Fewest-Most-Prices, position(Fewest, Most, Prices), Positions),

    % one 0/1 variable per player: 1 when the player is bought
    maplist([_-_-Prices, Buys]>>(length(Prices, N), length(Buys, N), Buys ins 0..1), Positions, Groups),

    % the number of players bought at each position lies within its limits
    maplist([Fewest-Most-_, Buys]>>(sum(Buys, #>=, Fewest), sum(Buys, #=<, Most)), Positions, Groups),

    % at least eleven players in total
    append(Groups, Bought),
    sum(Bought, #>=, MinPlayers),

    % Z = total price paid, and it stays within the budget
    findall(Price, (member(_-_-Prices, Positions), member(Price, Prices)), AllPrices),
    Z in 0..Budget,
    scalar_product(AllPrices, Bought, #=, Z).
