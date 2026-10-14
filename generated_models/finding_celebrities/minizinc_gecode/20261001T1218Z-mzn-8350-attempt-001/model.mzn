% Finding celebrities: at a party, graph[i,j] = 1 if guest i knows guest j.
% A celebrity is known by everybody at the party and knows only other
% celebrities. At least one celebrity is present. Report who is a celebrity.

array[int, int] of int: graph;  % who knows whom (a guest may "know" himself)

set of int: Guests = index_set_1of2(graph);
int: n = card(Guests);

% celebrities[i] = true if guest i is a celebrity
array[Guests] of var bool: celebrities;

% num_celebrities = how many celebrities there are; at least one is present
var 1..n: num_celebrities;
constraint num_celebrities = sum(i in Guests) (bool2int(celebrities[i]));

% A guest is a celebrity exactly when all n guests know him (his column of
% the graph sums to n) and he knows only celebrities (his row sums to the
% number of celebrities, since every celebrity is known by everybody).
constraint forall(i in Guests)
    (celebrities[i] <->
        (sum(j in Guests) (graph[j, i]) = n /\
         sum(j in Guests) (graph[i, j]) = num_celebrities));

solve satisfy;

output ["{\"celebrities\": [", join(", ", [show(bool2int(celebrities[i])) | i in Guests]), "]}"];
