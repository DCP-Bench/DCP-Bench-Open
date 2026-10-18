% Farmer and cows: a farmer has a number of cows, numbered 1 up to the total
% number of cows, and cow i gives i units of milk. He has a number of sons and
% distributes his cows to them according to a given distribution. The total
% milk of each son must be the same. Output cow_assignments: index = cow
% (0-based, cow index+1 is the cow number), value = son (0-based).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [cow_assignments-Assign], none) :-
    memberchk(num_cows-N, Instance),
    memberchk(num_sons-S, Instance),
    memberchk(cows_per_son-Dist, Instance),
    S1 is S - 1,
    Total is N*(N+1)//2,
    length(Assign, N),
    Assign :: 0..S1,
    % Cols[i][j] = 1 when cow i+1 goes to son j (one 0/1 flag per cow and son)
    ( for(_, 1, N), foreach(Col, Cols), param(S) do
        length(Col, S),
        Col :: 0..1
    ),
    % every cow goes to exactly one son, and its son number is the flag's index
    ( foreach(Col, Cols), foreach(X, Assign) do
        sum(Col) #= 1,
        cow_son(Col, X)
    ),
    % each son receives the number of cows given by the distribution
    ( for(J, 0, S1), foreach(D, Dist), param(Cols) do
        son_column(Cols, J, Bs),
        sum(Bs) #= D
    ),
    % all sons receive the same milk: the milk of each son times the number
    % of sons is the milk of all cows
    ( for(J, 0, S1), param(Cols, S, Total) do
        son_column(Cols, J, Bs),
        milk_of(Bs, M),
        S * M #= Total
    ),
    % the flags are grouped by son, one son after the other, largest cows first
    ( for(J, 0, S1), foreach(Group, Groups), param(Cols) do
        son_column(Cols, J, Bs),
        reverse(Bs, Group)
    ),
    flatten(Groups, Vars).

% labelling of the 0/1 flags: the flags of one son are fixed before the next son
search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_max, complete, []).

% the son of a cow, as a number, from its 0/1 flags
cow_son(Col, X) :-
    ( foreach(B, Col), count(J, 0, _), fromto(0, A0, A1, Sum) do
        A1 #= A0 + J * B
    ),
    X #= Sum.

% the flags of all cows for son J
son_column(Cols, J, Bs) :-
    ( foreach(Col, Cols), foreach(B, Bs), param(J) do
        nth0(J, Col, B)
    ).

% the milk of a son with cow flags Bs, cow i+1 gives i+1 units
milk_of(Bs, M) :-
    ( foreach(B, Bs), count(I, 1, _), fromto(0, A0, A1, Sum) do
        A1 #= A0 + I * B
    ),
    M #= Sum.
