:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Arch friends: the order in which Harriet bought four pairs of shoes and where
% she bought each.  Every variable holds a stop number from 1 to 4.
model(_Instance, Vars,
      [ecruespadrilles-Ecru, fuchsiaflats-Fuchsia, purplepumps-Purple,
       suedesandals-Suede, footfarm-FootFarm, heelsinahandcart-Heels,
       theshoepalace-Palace, tootsies-Tootsies]) :-
    Shoes = [Ecru, Fuchsia, Purple, Suede],
    Stores = [FootFarm, Heels, Palace, Tootsies],
    append(Shoes, Stores, Vars),
    Vars ins 1..4,
    all_distinct(Shoes),
    all_distinct(Stores),

    % 1. Fuchsia flats came from Heels in a Handcart.
    Fuchsia #= Heels,
    % 2. The stop after the purple pumps was not Tootsies.
    Purple + 1 #\= Tootsies,
    % 3. The Foot Farm was the second stop.
    FootFarm #= 2,
    % 4. The suede sandals came two stops after The Shoe Palace.
    Palace + 2 #= Suede.
