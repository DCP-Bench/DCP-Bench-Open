:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% De Bruijn sequence B(base, n): a cyclic sequence over an alphabet of `base`
% symbols, of length base^n, in which every string of n symbols occurs exactly
% once. Modelled as a cycle through all base^n windows of n consecutive symbols.
model(Instance, Vars, [de_bruijn-DeBruijn]) :-
    Base = Instance.base,    % size of the alphabet
    N = Instance.n,          % order: length of the strings that must all appear
    M is Base ^ N,           % length of the sequence = number of distinct strings
    Top is M - 1,
    Symbol is Base - 1,

    % X[i] = the number (in the given base) read from the window starting at position i
    length(X, M),
    X ins 0..Top,
    % Windows[i] = the symbols (most significant first) of the window starting at position i
    length(Windows, M),
    maplist({N, Symbol}/[Window]>>(length(Window, N), Window ins 0..Symbol), Windows),

    % every possible string occurs exactly once, i.e. all window numbers differ
    all_distinct(X),

    % link each window number to its symbols
    numlist(1, N, Places),
    maplist({Base, N}/[Place, Weight]>>(Weight is Base ^ (N - Place)), Places, Weights),
    maplist({Weights}/[Window, Number]>>scalar_product(Weights, Window, #=, Number), Windows, X),

    % consecutive windows overlap: window i shifted by one symbol is window i-1 ...
    Windows = [First|_],
    last(Windows, Final),
    consecutive(Windows),
    % ... and the last window continues into the first one, closing the cycle
    overlaps(Final, First),

    % the sequence is the first symbol of every window
    maplist([Window, Head]>>(Window = [Head|_]), Windows, DeBruijn),
    append(Windows, Cells),
    append(Cells, X, Vars).

% each window shifted left by one symbol is the start of the window that follows it
consecutive([_]).
consecutive([Before, After|Rest]) :-
    overlaps(Before, After),
    consecutive([After|Rest]).

overlaps([_|Tail], Next) :-
    append(Prefix, [_], Next),
    maplist(#=, Tail, Prefix).
