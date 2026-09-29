:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% N-puzzle (sliding tiles): list the board at each of N_STEPS steps, from the
% start state to the end state, where every step slides one tile into the empty
% square (0) and the board changes at each step.
model(Instance, Vars, [steps-Steps]) :-
    NSteps = Instance.'N_STEPS',       % boards in the solution, start and end included
    Start = Instance.puzzle_start,     % 0 marks the empty square
    End = Instance.puzzle_end,
    length(Start, Dim),
    Tiles is Dim * Dim - 1,            % e.g. 8 tiles for a 3 x 3 board
    Squares is Dim * Dim,

    % Steps[t] = the board at step t as a list of rows; Boards[t] is the same board flattened
    length(Steps, NSteps),
    maplist({Dim, Tiles}/[Board]>>(length(Board, Dim),
                                   maplist({Dim, Tiles}/[Row]>>(length(Row, Dim), Row ins 0..Tiles), Board)), Steps),
    maplist([Board, Flat]>>append(Board, Flat), Steps, Boards),

    % the first board is the start state and the last one the end state
    Steps = [Start|_],
    last(Steps, End),

    % for every square in row-major order, the squares that count as "here or
    % next to here" (flat positions counted from 1)
    findall(Around, (between(1, Dim, I), between(1, Dim, J),
                     findall(Q, (between(1, Dim, A), between(1, Dim, B),
                                 abs(A - I) + abs(B - J) =< 1, Q is (A - 1) * Dim + B), Around)),
            Neighbourhoods),

    successive(Boards, Neighbourhoods, Squares),
    append(Boards, Vars).

successive([_], _, _).
successive([Before, After|Rest], Neighbourhoods, Squares) :-
    % each board uses every tile once
    all_distinct(After),
    % which squares are empty before and after
    maplist([Tile, Empty]>>(Empty #<==> (Tile #= 0)), Before, EmptyBefore),
    maplist([Tile, Empty]>>(Empty #<==> (Tile #= 0)), After, EmptyAfter),
    % the empty square can only move to a neighbouring square: where it is empty
    % now it was empty here or on an adjacent square before
    maplist({EmptyBefore}/[Around, EmptyNow]>>(
                maplist({EmptyBefore}/[Q, E]>>nth1(Q, EmptyBefore, E), Around, AroundEmpty),
                sum(AroundEmpty, #=, HowManyAround),
                EmptyNow #==> (HowManyAround #>= 1)), Neighbourhoods, EmptyAfter),
    % only the empty square moves: a square that is neither empty before nor
    % empty after keeps its tile
    maplist([B, A, Same]>>(Same #<==> (B #= A)), Before, After, Sames),
    maplist([EB, EA, Same]>>(EB + EA + Same #>= 1), EmptyBefore, EmptyAfter, Sames),
    % the board must change at every step (no standing still)
    sum(Sames, #<, Squares),
    successive([After|Rest], Neighbourhoods, Squares).
