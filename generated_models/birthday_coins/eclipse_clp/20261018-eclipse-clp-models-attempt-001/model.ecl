% Birthday coins: Tommy got 15 coins (half-crowns, shillings, sixpences)
% totalling 1 pound 5 shillings 6 pence. Count the half-crowns.
% A half-crown is 30 pence, a shilling 12 pence, a sixpence 6 pence.

:- lib(ic).

model(_Instance, [H, S, P], [half_crowns-H], none) :-
    % Tommy was given 15 coins for his birthday
    [H, S, P] #:: 0..15,
    H + S + P #= 15,
    % he added it up to one pound, five shillings and six pence
    % (240 + 60 + 6 = 306 pence)
    30*H + 12*S + 6*P #= 306.
