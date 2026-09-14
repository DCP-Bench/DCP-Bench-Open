include "globals.mzn";

int: n;
int: c;

array[1..n] of var 1..c: balls;

constraint forall(x in 1..n-1, y in 1..n-x where x + y <= n) (
     balls[x] != balls[y]
  \/ balls[x] != balls[x + y]
  \/ balls[y] != balls[x + y]
);

solve satisfy;

output ["{\"balls\": [", join(", ", [show(balls[i]) | i in 1..n]), "]}"];
