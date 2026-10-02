% Initials queue: ten people stand in a queue. Each person's initials are an
% alphabetically ordered pair of distinct letters from A..E. No two people have
% the same initials, no one shares a letter with the person in front, BE is at
% the front, CD is second and BD is at the end. Find the queue.
include "globals.mzn";

% The problem statement fixes these constants; the instance carries no data.
int: n = 10;                       % people in the queue
int: A = 0; int: B = 1; int: C = 2; int: D = 3; int: E = 4;   % letters as numbers

% queue[i, 1], queue[i, 2] = the two initials of the person in position i (0 = A .. 4 = E)
array[1..n, 1..2] of var A..E: queue;

% the two initials of a person are alphabetically ordered (so also distinct)
constraint forall(i in 1..n) (queue[i, 1] < queue[i, 2]);

% no two people have the same initials: give each pair a code and require the codes
% to differ (same as comparing the pairs position by position)
array[1..n] of var 0..24: code;
constraint forall(i in 1..n) (code[i] = queue[i, 1] * 5 + queue[i, 2]);
constraint all_different(code);

% no one shares a letter with the person directly in front
constraint forall(i in 1..n-1, a in 1..2, b in 1..2) (queue[i, a] != queue[i + 1, b]);

% BE is at the front of the queue
constraint queue[1, 1] = B /\ queue[1, 2] = E;

% CD is right behind BE
constraint queue[2, 1] = C /\ queue[2, 2] = D;

% BD is at the end of the queue
constraint queue[n, 1] = B /\ queue[n, 2] = D;

solve satisfy;

output ["{\"queue\": [", join(", ", ["[" ++ show(queue[i, 1]) ++ ", " ++ show(queue[i, 2]) ++ "]" | i in 1..n]), "]}"];
