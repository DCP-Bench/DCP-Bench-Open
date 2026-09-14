:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [words-Words]) :-
    Length = Instance.n,
    Count = Instance.num_words,
    length(Words, Count),
    maplist({Length}/[Word]>>(length(Word, Length), Word ins 1..4), Words),
    append(Words, Vars),
    maplist(four_from_cg, Words),
    findall(I-J, (between(1, Count, I), Next is I + 1, between(Next, Count, J)), Distinct),
    maplist(far_apart(Words), Distinct),
    findall(I-J, (between(1, Count, I), between(1, Count, J)), Ordered),
    maplist(reverse_complement(Words), Ordered).

% Four of the letters are C or G, that is 2 or 3.
four_from_cg(Word) :-
    maplist([Letter, Is]>>(Is #<==> (Letter #= 2 #\/ Letter #= 3)), Word, Flags),
    sum(Flags, #=, 4).

far_apart(Words, I-J) :-
    nth1(I, Words, First),
    nth1(J, Words, Second),
    differences(First, Second, 4).

% The reverse of x and the complement of y differ in at least four positions.
reverse_complement(Words, I-J) :-
    nth1(I, Words, X),
    nth1(J, Words, Y),
    reverse(X, Reversed),
    maplist([Letter, Complement]>>(Complement #= 5 - Letter), Y, Complemented),
    differences(Reversed, Complemented, 4).

differences(Xs, Ys, Least) :-
    maplist([A, B, Differs]>>(Differs #<==> (A #\= B)), Xs, Ys, Flags),
    sum(Flags, #>=, Least).
