:- use_module(library(clpfd)).

% Huey, Dewey and Louie: three cub scouts are questioned about who is guilty.
% Each makes a statement and, being a cub scout, cannot lie, so all three
% statements are true. Decide who (if anyone) is guilty. The problem has no
% instance data. Each variable is 1 if that scout is guilty, 0 if not.
model(_Instance, Vars, [huey-Huey, dewey-Dewey, louie-Louie]) :-
    Vars = [Huey, Dewey, Louie],
    Vars ins 0..1,

    % Huey: Dewey and Louie have an equal share in it; if one is guilty, so is
    % the other.
    Dewey #= Louie,

    % Dewey: if Huey is guilty, then so am I.
    Huey #==> Dewey,

    % Louie: Dewey and I are not both guilty.
    #\ (Dewey #/\ Louie).
