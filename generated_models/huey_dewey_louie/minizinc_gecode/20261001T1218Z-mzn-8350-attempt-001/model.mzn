% Huey, Dewey and Louie: the uncle questions the three nephews, who are cub
% scouts and cannot tell a lie, so all their statements are true. Work out who
% is guilty. This problem has no instance data: the statements are part of the
% problem statement.

% huey, dewey, louie = true if that nephew is guilty
var bool: huey;
var bool: dewey;
var bool: louie;

% Huey: Dewey and Louie have an equal share in it; if one is guilty, so is the other.
constraint dewey <-> louie;

% Dewey: If Huey is guilty, then so am I.
constraint huey -> dewey;

% Louie: Dewey and I are not both guilty.
constraint not (dewey /\ louie);

solve satisfy;

output ["{\"huey\": ", show(huey), ", \"dewey\": ", show(dewey), ", \"louie\": ", show(louie), "}"];
