% The Zebra puzzle (Einstein's puzzle).
% Five houses in a row, numbered 0..4 from left to right. Each attribute
% variable holds the house number of the inhabitant or of the attribute value.

:- lib(ic).
:- lib(lists).

model(_Instance, Vars, Outputs) :-
    Colors = [Yellow, Green, Red, White, Blue],
    Nations = [Italy, Spain, Japan, England, Norway],
    Pets = [Cat, Zebra, Bear, Snails, Horse],
    Drinks = [Milk, Water, Tea, Coffee, Juice],
    Jobs = [Painter, Sculptor, Diplomat, Pianist, Doctor],
    flatten([Colors, Nations, Pets, Drinks, Jobs], Vars),
    Vars :: 0..4,

    % Each of the five houses is painted a different color, and has one inhabitant.
    % The inhabitants are all of different nationalities, own different pets,
    % drink different beverages and have different jobs.
    alldifferent(Colors),
    alldifferent(Nations),
    alldifferent(Pets),
    alldifferent(Drinks),
    alldifferent(Jobs),

    % the painter owns the horse
    Painter #= Horse,
    % the diplomat drinks coffee
    Diplomat #= Coffee,
    % the one who drinks milk lives in the white house
    Milk #= White,
    % the Spaniard is a painter
    Spain #= Painter,
    % the Englishman lives in the red house
    England #= Red,
    % the snails are owned by the sculptor
    Snails #= Sculptor,
    % the green house is immediately on the left of the red one
    Green + 1 #= Red,
    % the Norwegian lives immediately on the right of the blue house
    Norway #= Blue + 1,
    % the doctor drinks milk
    Doctor #= Milk,
    % the diplomat is Japanese
    Diplomat #= Japan,
    % the Norwegian owns the zebra
    Norway #= Zebra,
    % the green house is next to the white one
    abs(Green - White) #= 1,
    % the horse is owned by the neighbor of the diplomat
    abs(Horse - Diplomat) #= 1,
    % the Italian either lives in the red, white or green house
    (Italy #= Red) or (Italy #= White) or (Italy #= Green),

    Outputs = [colors-Colors, drinks-Drinks, jobs-Jobs, nations-Nations, pets-Pets].
