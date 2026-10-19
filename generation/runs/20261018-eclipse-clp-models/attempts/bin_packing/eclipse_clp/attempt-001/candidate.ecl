% Bin packing: items with weights are assigned to bins of a fixed capacity,
% so that the total weight of the items in each bin does not exceed the capacity.
% The output bins gives, for each item, the 0-based bin it is assigned to.

:- lib(ic).

model(Instance, Bins, [bins-Bins]) :-
    memberchk(weights-Ws, Instance),
    memberchk(capacity-C, Instance),
    memberchk(num_bins-B, Instance),
    length(Ws, N),
    length(Bins, N),

    % Each item is assigned to one bin, numbered from 0.
    Bins :: 0..B-1,

    % The total weight of the items in each bin does not exceed the capacity.
    ( for(K, 0, B-1), param(Bins, Ws, C) do
        ( foreach(W, Ws), foreach(X, Bins), foreach(T, Terms), param(K) do
            In #= (X #= K),
            T #= W * In
        ),
        sum(Terms) #=< C
    ).

search_goal(Bins) :-
    search(Bins, 0, first_fail, indomain_min, complete, []).
