:- use_module(library(clpfd)).

% Thick as thieves: after a robbery, Inspector Korner interviews six suspects
% (Artie, Bill, Crackitt, Dodgy, Edgy, Fingers). The getaway car held at most
% two, so at least four are innocent. The innocent tell the truth and the
% guilty lie. Find who is guilty. The problem has no instance data. Each
% variable is 1 if that suspect is guilty, 0 if not.
model(_Instance, Vars, [artie-Artie, bill-Bill, crackitt-Crackitt, dodgy-Dodgy,
                        edgy-Edgy, fingers-Fingers]) :-
    Vars = [Artie, Bill, Crackitt, Dodgy, Edgy, Fingers],
    Vars ins 0..1,

    % the getaway car held at most two, so at most two are guilty
    sum(Vars, #=, Guilty),
    Guilty #=< 2,

    % a suspect is guilty exactly when the statement made is false

    % Artie: "It wasn't me."
    lies_if_guilty(Artie, #\ Artie),

    % Bill: "Crackitt was in it up to his neck."
    lies_if_guilty(Bill, Crackitt),

    % Crackitt: "No I wasn't."
    lies_if_guilty(Crackitt, #\ Crackitt),

    % Dodgy: "If Crackitt did it, Bill did it with him."
    lies_if_guilty(Dodgy, Crackitt #==> Bill),

    % Edgy: "Nobody did it alone." (more than one is guilty)
    lies_if_guilty(Edgy, Guilty #> 1),

    % Fingers: "That's right: it was Artie and Dodgy together."
    lies_if_guilty(Fingers, Artie #/\ Dodgy).

% a suspect is guilty if and only if the statement he made is false
lies_if_guilty(Guilty, Statement) :-
    Guilty #<==> #\ Statement.
