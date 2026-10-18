% Finding celebrities at a party.
% Given a list of people at a party and for each person the list of people
% they know at the party, find the celebrities. A celebrity is a person that
% everybody at the party knows but that only knows other celebrities. At
% least one celebrity is present. Output: 0/1 per person, same order as input.

:- lib(ic).
:- lib(listut).

model(Instance, Cs, [celebrities-Cs]) :-
    memberchk(graph-G, Instance),
    length(G, N),
    length(Cs, N),
    Cs :: 0..1,

    % At least one celebrity is present at the party.
    sum(Cs) #>= 1,

    % A celebrity is a person that everybody at the party knows
    % (including the celebrity itself, as the diagonal of the data says).
    % Each person j that does not know i rules out i being a celebrity.
    % A celebrity only knows other celebrities: if i knows j then i being
    % a celebrity forces j to be a celebrity too.
    ( for(I, 1, N), param(G, Cs, N) do
        nth1(I, Cs, CI),
        ( for(J, 1, N), param(G, Cs, CI, I) do
            nth1(J, Cs, CJ),
            nth1(I, G, RowI),
            nth1(J, RowI, KnowsIJ),
            nth1(J, G, RowJ),
            nth1(I, RowJ, KnowsJI),
            % everybody knows the celebrity: j knows i
            CI #=< KnowsJI,
            % a celebrity only knows celebrities: i knows j implies j is a celebrity
            ( KnowsIJ =:= 1 -> CI #=< CJ ; true )
        )
    ).
