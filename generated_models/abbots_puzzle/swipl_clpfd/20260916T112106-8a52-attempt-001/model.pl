:- use_module(library(clpfd)).

% Abbot's puzzle: share 100 bushels among 100 people.  The problem carries no
% instance data of its own, so every number below is the puzzle statement.
model(_Instance, Vars, [men-Men, women-Women, children-Children]) :-
    Vars = [Men, Women, Children],
    Vars ins 0..100,
    % One hundred people in total.
    Men + Women + Children #= 100,
    % Three bushels a man, two a woman, half a bushel a child, doubled through
    % so the half stays an integer.
    Men * 6 + Women * 4 + Children #= 200,
    % Five times as many women as men.
    Men * 5 #= Women.
