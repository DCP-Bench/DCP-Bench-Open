:- use_module(library(clpfd)).

% Five floors: Baker, Cooper, Fletcher, Miller and Smith live on the first five
% floors of an apartment house, one person per floor. Find the floor of each
% person. The problem has no instance data. The outputs are named by the first
% letter of each person; floors are numbered 1 to 5.
model(_Instance, Vars, ['B'-B, 'C'-C, 'F'-F, 'M'-M, 'S'-S]) :-
    Vars = [B, C, F, M, S],
    Vars ins 1..5,

    % they all live on different floors
    all_distinct(Vars),

    % Baker does not live on the fifth floor.
    B #\= 5,

    % Cooper does not live on the first floor.
    C #\= 1,

    % Fletcher does not live on either the fifth or the first floor.
    F #\= 5,
    F #\= 1,

    % Miller lives on a higher floor than Cooper.
    M #> C,

    % Smith does not live on a floor adjacent to Fletcher's.
    abs(S - F) #\= 1,

    % Fletcher does not live on a floor adjacent to Cooper's.
    abs(F - C) #\= 1.
