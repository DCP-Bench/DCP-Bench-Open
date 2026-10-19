% twelve_pack: closest combination of packs that meets or exceeds a target.
% Given a target number of items and the sizes of the packs, choose how many
% packs of each size to use so that the total number of items is at least the
% target and as small as possible. Output counts: the number of packs of each
% size used.

:- lib(ic).

model(Instance, Cs, [counts-Cs], Objective) :-
    memberchk(packs-Packs, Instance),
    memberchk(target-Target, Instance),
    length(Packs, K),
    length(Cs, K),
    % number of packs of each size is between 0 and ceil(target / pack size);
    % one pack more than that already reaches the target on its own, so the
    % optimal combination never needs more (bound derived from the data)
    ( foreach(C, Cs), foreach(P, Packs), param(Target) do
        UB is (Target + P - 1) // P,
        C :: 0..UB
    ),
    % items in each pack size: packs of that size times pack size
    ( foreach(C, Cs), foreach(P, Packs), foreach(T, Terms) do
        T #= C * P
    ),
    Total #= sum(Terms),
    % the combination must meet or exceed the target
    Total #>= Target,
    % minimise the number of items bought, so the combination is as close to the target as possible
    Objective = min(Total).
