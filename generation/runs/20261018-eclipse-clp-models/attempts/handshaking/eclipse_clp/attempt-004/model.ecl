% Handshaking problem (Hilary and Jocelyn): Hilary and Jocelyn are married and invite
% num_couples couples. Persons 1..P, P = 2*(num_couples+1); persons 2k-1 and 2k are a
% married couple. Hilary is person 1, Jocelyn is person 2. Output: hands Hilary shook.
:- lib(ic).
:- lib(ic_global_gac).

model(Instance, [Hil|Rest], [hil-Hil]) :-
    memberchk(num_couples-N, Instance),
    P is 2*N + 2,
    Max is P - 2,
    dim(H, [P, P]),
    % Shaking hands is mutual (one 0/1 variable per unordered pair); nobody shakes
    % hands with him or herself.
    ( for(I, 1, P), param(H, P) do
        ( for(J, 1, P), param(H, I) do
            ( J > I -> arg([I,J], H, C), C :: 0..1, arg([J,I], H, C)
            ; J =:= I -> arg([I,J], H, 0)
            ; true )
        )
    ),
    % Nobody shakes hands with his or her spouse.
    ( for(K, 1, N+1), param(H) do
        A is 2*K - 1, B is 2*K,
        arg([A,B], H, 0)
    ),
    % Hands[I] is the number of hands person I has shaken: the sum of row I.
    ( for(I, 1, P), foreach(Hd, Hands), param(H, P, Max) do
        Hd :: 0..Max,
        collection_to_list(H[I,1..P], Row),
        Hd #= sum(Row)
    ),
    % Jocelyn asks everyone else how many hands they shook, and all the answers are
    % different.
    Hands = [Hil, Joc | Guests],
    ic_global_gac:alldifferent([Hil|Guests]),
    % Implied constraint derived from the description: the P-1 = 2n+1 different answers
    % lie in 0..2n, so they are exactly 0..2n. The person with 2n shook hands with all but
    % his or her spouse, so only the spouse can have shaken 0. Remove that couple and
    % repeat: the two members of each invited couple have answers summing to 2n.
    couple_sums(Guests, Max),
    flatten_array(H, Cells0),
    term_variables(Cells0, Cells),
    append(Guests, [Joc|Cells], Rest).

% The answers of the two members of a couple add up to Max and differ (domain-consistent
% table, so Hilary's value removes its complement from the other couples).
couple_sums([], _).
couple_sums([X,Y|T], Max) :-
    ( for(A, 0, Max), fromto([], R0, R1, Rows), param(Max) do
        B is Max - A,
        ( A =\= B -> R1 = [[A,B]|R0] ; R1 = R0 )
    ),
    ic_mdd:table([[X,Y]], Rows),
    couple_sums(T, Max).

% Hilary's count is labelled first, outside once/1, so every value of it is tried and the
% driver sees each output. The remaining variables (guests' counts, Jocelyn, cells) cannot
% change the declared output hil, so once/1 keeps one witness for each value of hil.
search_goal([Hil|Rest]) :-
    indomain(Hil),
    once(search(Rest, 0, input_order, indomain_min, complete, [])).
