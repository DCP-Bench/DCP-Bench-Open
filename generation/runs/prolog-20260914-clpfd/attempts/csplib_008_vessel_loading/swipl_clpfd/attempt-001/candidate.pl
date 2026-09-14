:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [left-Lefts, right-Rights, top-Tops, bottom-Bottoms]) :-
    Width = Instance.deck_width,
    Length = Instance.deck_length,
    N = Instance.n_containers,
    Widths = Instance.width,
    Lengths = Instance.length,
    Classes = Instance.classes,
    Separation = Instance.separation,
    length(Lefts, N), length(Rights, N), length(Tops, N), length(Bottoms, N),
    Lefts ins 0..Width, Rights ins 0..Width,
    Tops ins 0..Length, Bottoms ins 0..Length,
    maplist(placed, Lefts, Rights, Tops, Bottoms, Widths, Lengths),
    findall(X-Y, (between(1, N, X), Next is X + 1, between(Next, N, Y)), Pairs),
    maplist(separated(Lefts, Rights, Tops, Bottoms, Classes, Separation), Pairs),
    append([Lefts, Rights, Tops, Bottoms], Vars).

% Either orientation of the container.
placed(Left, Right, Top, Bottom, W, L) :-
    (Right - Left #= W #/\ Top - Bottom #= L) #\/ (Right - Left #= L #/\ Top - Bottom #= W).

separated(Lefts, Rights, Tops, Bottoms, Classes, Separation, X-Y) :-
    nth1(X, Classes, ClassX),
    nth1(Y, Classes, ClassY),
    nth1(ClassX, Separation, Row),
    nth1(ClassY, Row, Sep),
    nth1(X, Lefts, LeftX), nth1(X, Rights, RightX),
    nth1(X, Tops, TopX), nth1(X, Bottoms, BottomX),
    nth1(Y, Lefts, LeftY), nth1(Y, Rights, RightY),
    nth1(Y, Tops, TopY), nth1(Y, Bottoms, BottomY),
    (RightX + Sep #=< LeftY) #\/ (LeftX #>= RightY + Sep)
      #\/ (TopX + Sep #=< BottomY) #\/ (BottomX #>= TopY + Sep).
