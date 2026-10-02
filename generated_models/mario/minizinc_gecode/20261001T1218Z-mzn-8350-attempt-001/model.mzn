% Mario: collect as much gold as possible by visiting houses. Mario starts at
% his own house and ends at Luigi's house; travelling between houses uses fuel
% and Mario has a limited amount. The route is reported as the successor of
% each house, with s[i] = i for a house that is not visited and Luigi's house
% followed by Mario's, which closes the route into a cycle.
include "globals.mzn";

int: nHouses;
int: marioHouse;                    % 0-indexed in the data
int: luigiHouse;                    % 0-indexed in the data
int: fuelLimit;                     % fuel Mario has
array[int, int] of int: arc_fuel;   % arc_fuel[i, j] = fuel to go from house i to house j
array[int] of int: goldInHouse;     % gold in each house

% The data counts houses from 0; this model counts them from 1 (MiniZinc
% arrays start at 1) and subtracts 1 again when writing the answer.
set of int: Houses = 1..nHouses;
int: mario = marioHouse + 1;
int: luigi = luigiHouse + 1;

% s[i] = the house visited after house i; s[i] = i if house i is not visited
array[Houses] of var Houses: s;

% The visited houses form one single route that closes into a cycle, and the
% houses that are not visited point to themselves. (The reference ranks the
% houses along the route to rule out separate loops; the subcircuit constraint
% says the same without extra ranking variables that would leave the ranks of
% unvisited houses free.)
constraint subcircuit(s);

% Mario's house is on the route and Luigi's house is its last stop, followed by Mario's house
constraint s[mario] != mario;
constraint s[luigi] = mario;

% total fuel used by the arcs of the route; a house that is not visited has
% s[i] = i and arc_fuel[i, i] = 0, so it costs nothing
constraint sum(i in Houses) (arc_fuel[i, s[i]]) <= fuelLimit;

% gold collected = gold of the houses that are visited (s[i] != i)
var int: gold = sum(i in Houses) (if s[i] != i then goldInHouse[i] else 0 endif);

% maximise the gold collected
var int: objective = gold;
solve maximize objective;

output ["{\"s\": [", join(", ", [show(s[i] - 1) | i in Houses]), "]}"];
