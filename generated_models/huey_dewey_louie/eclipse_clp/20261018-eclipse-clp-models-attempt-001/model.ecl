% Huey, Dewey and Louie: the uncle knows they cannot tell a lie, so every
% statement they make is true. Decide who (if any) is guilty.
%   Huey:  Dewey and Louie has equal share in it; if one is guilty, so is the other.
%   Dewey: If Huey is guilty, then so am I.
%   Louie: Dewey and I are not both guilty.
% Booleans are 0/1: H = Huey guilty, D = Dewey guilty, L = Louie guilty.

:- lib(ic).

model(_Instance, [H, D, L], [huey-H, dewey-D, louie-L]) :-
    [H, D, L] #:: 0..1,

    % Huey: Dewey and Louie has equal share in it; if one is guilty, so is the other.
    D #= L,

    % Dewey: If Huey is guilty, then so am I.
    H #=< D,

    % Louie: Dewey and I are not both guilty.
    D + L #=< 1.
