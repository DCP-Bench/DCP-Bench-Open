% Arch friends: Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats,
% purple pumps, suede sandals) at four stores (Foot Farm, Heels in a Handcart,
% The Shoe Palace, Tootsies), one purchase per stop, stops numbered 1 to 4.
% Find the stop of each shoe and the stop of each store.

:- lib(ic).

model(_Instance, [E, F, P, S, FF, HH, PS, T],
      [ecruespadrilles-E, fuchsiaflats-F, purplepumps-P, suedesandals-S,
       footfarm-FF, heelsinahandcart-HH, theshoepalace-PS, tootsies-T]) :-

    % values are integers from 1 to 4 (the four stops); the same value denotes the
    % same shoe or store, so each group of four takes four different stops
    [E, F, P, S] :: 1..4,
    [FF, HH, PS, T] :: 1..4,
    alldifferent([E, F, P, S]),
    alldifferent([FF, HH, PS, T]),

    % Harriet bought fuchsia flats at Heels in a Handcart.
    F #= HH,

    % The store she visited just after buying her purple pumps was not Tootsies.
    T #\= P + 1,

    % The Foot Farm was Harriet's second stop.
    FF #= 2,

    % Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    S #= PS + 2.
