% Airline crew rostering: staff every flight with the right size and skill mix,
% and give anyone who flies a break of two flights afterwards.
include "globals.mzn";

array[int, int] of int: attributes;
array[int, int] of int: required_crew;

set of int: Persons = index_set_1of2(attributes);
set of int: Skills = index_set_2of2(attributes);
set of int: Flights = index_set_1of2(required_crew);

array[Flights, Persons] of var bool: crew;

% Crew size, then one count per required skill. The requirement row is the
% crew size followed by the same five skill counts the attribute columns hold.
constraint forall(f in Flights) (
    sum(p in Persons) (bool2int(crew[f, p])) = required_crew[f, min(Skills)]
);
constraint forall(f in Flights, j in Skills) (
    sum(p in Persons) (attributes[p, j] * bool2int(crew[f, p]))
      >= required_crew[f, j + 1]
);

% After a flight, two flights off.
constraint forall(f in Flights, p in Persons where f + 2 <= max(Flights)) (
    bool2int(crew[f, p]) + bool2int(crew[f + 1, p]) + bool2int(crew[f + 2, p]) <= 1
);

% The reference pins the number of people who fly at least once to a variable
% whose domain starts at one, so at least one person flies. Stated as an
% equivalence rather than a one-sided bound, which flattens soundly.
array[Persons] of var bool: works;
constraint forall(p in Persons) (
    works[p] <-> exists(f in Flights) (crew[f, p])
);
constraint sum(p in Persons) (bool2int(works[p])) >= 1;

solve satisfy;

output ["{\"crew\": [",
        join(", ", [ "[" ++ join(", ", [show(crew[f, p]) | p in Persons]) ++ "]"
                   | f in Flights ]),
        "]}"];
