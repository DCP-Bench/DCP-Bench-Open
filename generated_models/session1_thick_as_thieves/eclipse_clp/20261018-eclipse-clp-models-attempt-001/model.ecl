% Thick as thieves: six suspects (artie, bill, crackitt, dodgy, edgy, fingers).
% Each Boolean says whether the suspect is guilty (1) or innocent (0).
% The innocent tell the truth and the guilty lie. Decide who is guilty.

:- lib(ic).

model(_Instance, [A, B, C, D, E, F],
      [artie-A, bill-B, crackitt-C, dodgy-D, edgy-E, fingers-F]) :-
    [A, B, C, D, E, F] :: 0..1,

    % the getaway car was barely big enough to hold two, and at least four were innocent
    % (one or ones guilty: at least one guilty, at most two)
    sum([A, B, C, D, E, F]) #>= 1,
    sum([A, B, C, D, E, F]) #=< 2,

    % the innocent ones tell the truth, while the guilty one or ones lie
    % ARTIE: "It wasn't me."
    ((A #= 0) <=> (A #= 0)),
    % BILL: "Crackitt was in it up to his neck."
    ((C #= 1) <=> (B #= 0)),
    % CRACKITT: "No I wasn't."
    ((C #= 0) <=> (C #= 0)),
    % DODGY: "If Crackitt did it, Bill did it with him."
    (((C #= 1) => (B #= 1)) <=> (D #= 0)),
    % EDGY: "Nobody did it alone."
    ((sum([A, B, C, D, E, F]) #\= 1) <=> (E #= 0)),
    % FINGERS: "That's right: it was Artie and Dodgy together."
    (((A #= 1) and (D #= 1)) <=> (F #= 0)).
