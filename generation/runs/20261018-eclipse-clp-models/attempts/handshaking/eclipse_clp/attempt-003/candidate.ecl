% Handshaking problem (Hilary and Jocelyn).
% Hilary and Jocelyn are married. They invite num_couples couples who are friends.
% The guests are persons 1..P with P = 2*(num_couples+1): persons 2k-1 and 2k are a
% married couple. Hilary is person 1 and Jocelyn is person 2.
:- lib(gfd).

model(Instance, Vars, [hil-Hil]) :-
    memberchk(num_couples-N, Instance),
    M is N + 1,
    P is 2*M,
    Max is P - 2,
    dim(H, [P, P]),
    % Each cell H[I,J] is 1 when person I and person J shake hands, 0 otherwise.
    ( multifor([I, J], 1, [P, P]), param(H) do
        H[I,J] :: 0..1
    ),

    % Shaking hands is mutual: H[I,J] = H[J,I].
    ( multifor([I, J], 1, [P, P]), param(H) do
        H[I,J] #= H[J,I]
    ),

    % Nobody shakes hands with him or herself or with his or her spouse.
    ( for(I, 1, P), param(H) do
        spouse(I, S),
        H[I,I] #= 0,
        H[I,S] #= 0
    ),

    % Hands[I] is the number of hands person I has shaken: the sum of row I.
    ( for(I, 1, P), foreach(Hand, Hands), param(H, P, Max) do
        collection_to_list(H[I,1..P], Row),
        Hand #= sum(Row),
        Hand :: 0..Max
    ),

    % All the answers are different. Jocelyn asks how many hands each person has
    % shaken, so the answers of the persons other than Jocelyn are all different.
    Hands = [Hil, _Jocelyn | Others],
    alldifferent([Hil | Others]),

    flatten_array(H, Cells),
    append(Hands, Cells, Vars).

% Hand counts first, largest value first, then the handshakes they come from.
% The hand counts are the first P entries of Vars, P + P*P = length(Vars).
search_goal(Vars) :-
    length(Vars, L),
    P is integer(round((sqrt(1 + 4*L) - 1) / 2)),
    length(Hands, P),
    append(Hands, Cells, Vars),
    search(Hands, 0, first_fail, indomain_max, complete, []),
    search(Cells, 0, first_fail, indomain_min, complete, []).

spouse(I, S) :-
    ( I mod 2 =:= 1 -> S is I + 1 ; S is I - 1 ).
