% Fifty puzzle (side show with dummies): choose which dummies are knocked over
% so that the sum of their numbers is exactly the target sum.
% Output: dummies, one 0/1 (Boolean) per dummy, 1 when the dummy is knocked over.

:- lib(ic).

model(Instance, Bs, [dummies-Bs], none) :-
    memberchk(target_sum-Target, Instance),
    memberchk(values-Values, Instance),
    length(Values, N),
    length(Bs, N),
    Bs :: 0..1,

    % The sum of the numbers on the men that you knock down is exactly the target sum,
    % neither more nor less.
    ( foreach(V, Values), foreach(B, Bs), foreach(T, Terms) do T #= V * B ),
    sum(Terms) #= Target.
