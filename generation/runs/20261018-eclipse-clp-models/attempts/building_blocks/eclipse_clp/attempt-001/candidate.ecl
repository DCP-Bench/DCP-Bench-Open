% Building blocks: alphabet blocks, each with one letter on each side.
% Find, for each letter of the alphabet, the block it is placed on (dice),
% such that every word of the given list can be spelled by the blocks.

:- lib(ic).
:- lib(listut).

model(Instance, Ds, [dice-Ds]) :-
    memberchk(num_blocks-NB, Instance),
    memberchk(num_sides-NS, Instance),
    memberchk(num_letters-NL, Instance),
    memberchk(alphabet-Alpha, Instance),
    memberchk(words_str-Words, Instance),
    NB1 is NB - 1,
    length(Ds, NL),
    Ds :: 0..NB1,

    % Each block has a single letter on each of its sides, so exactly num_sides letters sit on each block.
    ( for(B, 0, NB1), param(Ds, NS) do
        count_block(Ds, B, NS)
    ),

    % Each word is spelled by blocks: its letters must sit on different blocks, since a block shows one side at a time.
    ( foreach(W, Words), param(Alpha, Ds) do
        string_list(W, Cs),
        ( foreach(C, Cs), foreach(D, Dv), param(Alpha, Ds) do
            letter_index(Alpha, C, I),
            nth0(I, Ds, D)
        ),
        alldifferent(Dv)
    ).

% Exactly NS of the letters are placed on block B.
count_block(Ds, B, NS) :-
    ( foreach(D, Ds), foreach(Bi, Bs), param(B) do
        Bi #= (D #= B)
    ),
    sum(Bs) #= NS.

% Index (0-based) of letter code C in the alphabet string.
letter_index(Alpha, C, I) :-
    string_list(Alpha, As),
    nth0(I, As, C),
    !.
