:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% Frog circle: cards 1..n sit on a circle. A frog starts on card 1 and, from a
% card k, jumps k places clockwise. Arrange the cards so that the frog lands on
% every card.
model(Instance, Vars, [x-Cards]) :-
    N = Instance.n,                         % number of cards and of places
    Last is N - 1,

    % Cards[p] is the card lying at place p (places are 0-based in the problem,
    % so place p is the (p+1)-th element of the list).
    length(Cards, N),
    Cards ins 1..N,
    % every card appears exactly once on the circle
    all_distinct(Cards),
    % the frog starts on card 1, at place 0
    Cards = [First|_],
    First #= 1,

    % Places[i] is the place the frog stands on after i jumps, and Visited[i]
    % the card lying there.
    length(Places, N),
    Places ins 0..Last,
    length(Visited, N),
    Visited ins 1..N,
    Places = [0|_],
    Visited = [1|_],
    % each jump moves clockwise by the number on the card the frog stands on,
    % wrapping around the circle
    jumps(Places, Cards, N),
    % the frog never stands on the same place twice
    all_distinct(Places),
    % the card visited at step i is the card lying at that place
    visits(Places, Cards, Visited),
    % ...and the frog lands on every card
    all_distinct(Visited),

    % Search along the frog's path: choose the place of jump 1, then of jump 2,
    % ... Every choice fixes the card the frog jumped from.
    append(Places, Cards, Vars).

% A jump goes from the current place to the next place, which is the current
% place plus the number on the card lying there, modulo the number of places.
% The modulo is written as Place + Card = Next + Wrap * N with Wrap in 0..1 (the
% sum is below 2N), so that fixing two places also fixes the card in between.
jumps([_], _, _).
jumps([Place, Next|Places], Cards, N) :-
    Index #= Place + 1,
    element(Index, Cards, Card),
    Wrap in 0..1,
    Place + Card #= Next + Wrap * N,
    jumps([Next|Places], Cards, N).

% The card visited after a jump is the card at the place reached.
visits([], _, []).
visits([Place|Places], Cards, [Card|Visited]) :-
    Index #= Place + 1,
    element(Index, Cards, Card),
    visits(Places, Cards, Visited).
