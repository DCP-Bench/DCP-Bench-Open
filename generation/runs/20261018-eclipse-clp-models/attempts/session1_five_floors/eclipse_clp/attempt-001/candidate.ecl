% Five Floors puzzle: Baker, Cooper, Fletcher, Miller and Smith live on the
% first five floors of an apartment house. Find the floor of each person.
% Outputs: B (Baker), C (Cooper), F (Fletcher), M (Miller), S (Smith).

:- lib(ic).

model(_Instance, [B, C, F, M, S], ['B'-B, 'C'-C, 'F'-F, 'M'-M, 'S'-S]) :-
    % They all live on different floors.
    [B, C, F, M, S] :: 1..5,
    alldifferent([B, C, F, M, S]),

    % Baker does not live on the fifth floor.
    B #\= 5,

    % Cooper does not live on the first floor.
    C #\= 1,

    % Fletcher does not live on either the fifth or the first floor.
    F #\= 5,
    F #\= 1,

    % Miller lives on a higher floor than does Cooper.
    M #> C,

    % Smith does not live on a floor adjacent to Fletcher's.
    abs(S - F) #\= 1,

    % Fletcher does not live on a floor adjacent to Cooper's.
    abs(F - C) #\= 1.
