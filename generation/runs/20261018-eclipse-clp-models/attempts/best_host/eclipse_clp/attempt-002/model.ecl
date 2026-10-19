% best_host: seat six dinner guests around a round table so that no two adjacent
% guests are ones who do not get along (no conflict at dinner).
% Guests: 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
% Output x: the guest in each of the six seats, in seating order.

:- lib(ic).

% Each guest will only sit next to the guests listed for them in the description.
% Row A, column B of Table is 1 when B may sit next to A, and 0 otherwise.
friend_table([
    0,0,0,1,0,1,    % Andrew will only sit next to Dave and Frank
    0,0,1,0,1,0,    % Betty will only sit next to Cara and Erica
    0,1,0,0,0,1,    % Cara will only sit next to Betty and Frank
    1,0,0,0,1,0,    % Dave will only sit next to Andrew and Erica
    0,1,0,1,0,0,    % Erica will only sit next to Betty and Dave
    1,0,1,0,0,0     % Frank will only sit next to Andrew and Cara
]).

% A conflict arises when two guests who do not get along sit next to each other.
% Each adjacent pair must not conflict, so the pair must be an allowed neighbour.
pair_ok(A, B, Table) :-
    Idx #= A * 6 + B + 1,
    element(Idx, Table, 1).

model(_Instance, Xs, [x-Xs]) :-
    Xs = [X1, X2, X3, X4, X5, X6],
    Xs :: 0..5,
    % The guests occupy the six seats, each guest exactly once.
    alldifferent(Xs),
    friend_table(Table),
    % The table is round: each seat sits next to the following seat and the last seat sits next to the first.
    % If two guests who do not get along are seated next to each other, it will create conflict at dinner.
    pair_ok(X1, X2, Table),
    pair_ok(X2, X3, Table),
    pair_ok(X3, X4, Table),
    pair_ok(X4, X5, Table),
    pair_ok(X5, X6, Table),
    pair_ok(X6, X1, Table).
