:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [left-Lefts, right-Rights, top-Tops, bottom-Bottoms]) :-
    Width = Instance.deck_width,
    Length = Instance.deck_length,
    N = Instance.n_containers,
    Deck = deck(Lefts, Rights, Tops, Bottoms),
    length(Lefts, N), length(Rights, N), length(Tops, N), length(Bottoms, N),
    Lefts ins 0..Width, Rights ins 0..Width,
    Tops ins 0..Length, Bottoms ins 0..Length,
    % maplist/5 is the widest there is, so anything walking more lists than that
    % maps over the indices and reads each list with nth1/3.
    numlist(1, N, Containers),
    maplist({Deck, Instance}/[I]>>placed(Deck, Instance, I), Containers),
    findall(X-Y, (between(1, N, X), Next is X + 1, between(Next, N, Y)), Pairs),
    maplist({Deck, Instance}/[Pair]>>separated(Deck, Instance, Pair), Pairs),
    append([Lefts, Rights, Tops, Bottoms], Vars).

% Either orientation of the container.
placed(Deck, Instance, I) :-
    corners(Deck, I, Left, Right, Top, Bottom),
    nth1(I, Instance.width, W),
    nth1(I, Instance.length, L),
    (Right - Left #= W #/\ Top - Bottom #= L) #\/ (Right - Left #= L #/\ Top - Bottom #= W).

separated(Deck, Instance, X-Y) :-
    separation(Instance, X, Y, Sep),
    corners(Deck, X, LeftX, RightX, TopX, BottomX),
    corners(Deck, Y, LeftY, RightY, TopY, BottomY),
    (RightX + Sep #=< LeftY) #\/ (LeftX #>= RightY + Sep)
      #\/ (TopX + Sep #=< BottomY) #\/ (BottomX #>= TopY + Sep).

separation(Instance, X, Y, Sep) :-
    nth1(X, Instance.classes, ClassX),
    nth1(Y, Instance.classes, ClassY),
    nth1(ClassX, Instance.separation, Row),
    nth1(ClassY, Row, Sep).

corners(deck(Lefts, Rights, Tops, Bottoms), I, Left, Right, Top, Bottom) :-
    nth1(I, Lefts, Left),
    nth1(I, Rights, Right),
    nth1(I, Tops, Top),
    nth1(I, Bottoms, Bottom).
