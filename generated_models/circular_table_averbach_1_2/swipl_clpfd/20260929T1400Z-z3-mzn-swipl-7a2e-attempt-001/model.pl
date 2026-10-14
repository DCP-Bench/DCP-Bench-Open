:- use_module(library(clpfd)).

% Averbach's card-passing riddle: three players X, Y, Z of three different
% nationalities (American, English, French) sit round a table, each passing
% three cards to the person on their right. Y passed to the American, and X
% passed to the person who passed to the Frenchwoman. Find who is who.
% A seat is 0, 1 or 2 and seat b+1 (mod 3) is to the right of seat b.
%
% The riddle fixes everything; the instance carries no data.
model(_Instance, Vars,
      [x-X, y-Y, z-Z, american-American, english-English, french-French]) :-
    Vars = [X, Y, Z, American, English, French],
    Vars ins 0..2,
    % seats of the three players are all different
    all_different([X, Y, Z]),
    % seats of the three nationalities are all different: the same seat number in
    % the player and nationality outputs denotes the same person
    all_different([American, English, French]),
    % the American sits to the right of Y, since Y passed to the American
    American #= (Y + 1) mod 3,
    % X sits to the right of the Frenchwoman, since X passed to the person who passed to her
    X #= (French + 1) mod 3.
