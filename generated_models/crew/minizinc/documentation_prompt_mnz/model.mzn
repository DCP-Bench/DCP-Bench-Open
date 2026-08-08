include "globals.mzn";

% Input data
int: num_crew = 20;
int: num_flights = 10;

array[1..num_crew, 1..5] of int: attributes = [
    % steward, hostess, french, spanish, german
    [1, 0, 0, 0, 1],  % Tom     = 1
    [1, 0, 0, 0, 0],  % David   = 2
    [1, 0, 0, 0, 1],  % Jeremy  = 3
    [1, 0, 0, 0, 0],  % Ron     = 4
    [1, 0, 0, 1, 0],  % Joe     = 5
    [1, 0, 1, 1, 0],  % Bill    = 6
    [1, 0, 0, 1, 0],  % Fred    = 7
    [1, 0, 0, 0, 0],  % Bob     = 8
    [1, 0, 0, 1, 1],  % Mario   = 9
    [1, 0, 0, 0, 0],  % Ed      = 10
    [0, 1, 0, 0, 0],  % Carol   = 11
    [0, 1, 0, 0, 0],  % Janet   = 12
    [0, 1, 0, 0, 0],  % Tracy   = 13
    [0, 1, 0, 1, 1],  % Marilyn = 14
    [0, 1, 0, 0, 0],  % Carolyn = 15
    [0, 1, 0, 0, 0],  % Cathy   = 16
    [0, 1, 1, 1, 1],  % Inez    = 17
    [0, 1, 1, 0, 0],  % Jean    = 18
    [0, 1, 0, 1, 1],  % Heather = 19
    [0, 1, 1, 0, 0]   % Juliet  = 20
];

array[1..num_flights, 1..6] of int: required_crew = [
    % staff, stewards, hostesses, french, spanish, german
    [4, 1, 1, 1, 1, 1],  % Flight 1
    [5, 1, 1, 1, 1, 1],  % Flight 2
    [5, 1, 1, 1, 1, 1],  % Flight 3
    [6, 2, 2, 1, 1, 1],  % Flight 4
    [7, 3, 3, 1, 1, 1],  % Flight 5
    [4, 1, 1, 1, 1, 1],  % Flight 6
    [5, 1, 1, 1, 1, 1],  % Flight 7
    [6, 1, 1, 1, 1, 1],  % Flight 8
    [6, 2, 2, 1, 1, 1],  % Flight 9
    [7, 3, 3, 1, 1, 1]   % Flight 10
];

% Decision variables
% crew[f, c] = 1 if crew member c is assigned to flight f, else 0
array[1..num_flights, 1..num_crew] of var 0..1: crew;

% Constraints

% 1) Each flight must have the required number of total crew
constraint
  forall(f in 1..num_flights) (
    sum(c in 1..num_crew)(crew[f,c]) == required_crew[f,1]
  );

% 2) Each flight must have the required number of stewards
constraint
  forall(f in 1..num_flights) (
    sum(c in 1..num_crew)(crew[f,c] * attributes[c,1]) >= required_crew[f,2]
  );

% 3) Each flight must have the required number of hostesses
constraint
  forall(f in 1..num_flights) (
    sum(c in 1..num_crew)(crew[f,c] * attributes[c,2]) >= required_crew[f,3]
  );

% 4) Each flight must have the required number of French speakers
constraint
  forall(f in 1..num_flights) (
    sum(c in 1..num_crew)(crew[f,c] * attributes[c,3]) >= required_crew[f,4]
  );

% 5) Each flight must have the required number of Spanish speakers
constraint
  forall(f in 1..num_flights) (
    sum(c in 1..num_crew)(crew[f,c] * attributes[c,4]) >= required_crew[f,5]
  );

% 6) Each flight must have the required number of German speakers
constraint
  forall(f in 1..num_flights) (
    sum(c in 1..num_crew)(crew[f,c] * attributes[c,5]) >= required_crew[f,6]
  );

% 7) Each crew member has two flights off after an attended flight
% This means if crew member c attends flight f, then they cannot attend flights f+1 and f+2
constraint
  forall(c in 1..num_crew, f in 1..num_flights) (
    if f <= num_flights - 2 then
      crew[f,c] + crew[f+1,c] + crew[f+2,c] <= 1
    else if f = num_flights - 1 then
      crew[f,c] + crew[f+1,c] <= 1
    else
      true
    endif endif
  );

solve satisfy;

output [
  "{\n",
  "  \"crew\": [\n",
  join(",\n", [
    "    [" ++ join(", ", [show(crew[f,c]) | c in 1..num_crew]) ++ "]"
    | f in 1..num_flights
  ]),
  "\n  ]\n",
  "}"
];