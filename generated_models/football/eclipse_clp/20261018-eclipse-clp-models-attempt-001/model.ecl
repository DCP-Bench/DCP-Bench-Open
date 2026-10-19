% Football team selection: spend as much money as possible on a squad of
% players without going over GBP 30 million. Prices are in GBP thousands
% (the description's GBP millions times 1000) so all arithmetic is integer.
%
% Each player is a 0/1 selection variable. Output z is the total price of
% the selected players in GBP thousands.

:- lib(ic).

% Statistics show that, in the Premiership, there is a strong correlation
% between the value of a team's players and their final position in that
% league - so you want to spend as much money as you can.
% The chairman gives you an upper limit of GBP 30 million - so you want
% your purchases to add up to as close to that figure as possible (without
% going over).

model(_Instance, Vars, [z-Z], max(Z)) :-
    Goalkeeper = [730, 1280, 3880],
    Defender   = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],
    Midfielder = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],
    Striker    = [4460, 6470, 7780, 8390, 9500],
    length(Goalkeeper, NG), length(Defender, ND),
    length(Midfielder, NM), length(Striker, NS),
    length(Gs, NG), length(Ds, ND), length(Ms, NM), length(Ss, NS),
    Gs :: 0..1, Ds :: 0..1, Ms :: 0..1, Ss :: 0..1,
    append(Gs, Ds, GD), append(GD, Ms, GDM), append(GDM, Ss, Vars),

    % Goalkeepers (must buy 1 exactly):
    sum(Gs) #= 1,

    % Defenders (must buy 2 or more):
    sum(Ds) #>= 2,

    % Midfielders (must buy 3 or more):
    sum(Ms) #>= 3,

    % Strikers (must buy 2 or more):
    sum(Ss) #>= 2,

    % Also, you must buy at least eleven players in total.
    sum(Vars) #>= 11,

    % Print out the total price of the players you have selected (z) in GBP
    % thousands.
    weighted_terms(Goalkeeper, Gs, GT),
    weighted_terms(Defender, Ds, DT),
    weighted_terms(Midfielder, Ms, MT),
    weighted_terms(Striker, Ss, ST),
    append(GT, DT, GTD), append(GTD, MT, GTDM), append(GTDM, ST, Terms),
    sum(Terms) #= Z,

    % The chairman gives you an upper limit of GBP 30 million (30000 thousands).
    Z #=< 30000.

% weighted_terms(+Prices, +Selections, -Terms): the list of price * selection terms.
weighted_terms([], [], []).
weighted_terms([P|Ps], [X|Xs], [P*X|Ts]) :-
    weighted_terms(Ps, Xs, Ts).
