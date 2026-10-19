% Handshaking problem (Hilary and Jocelyn).
% Hilary and Jocelyn are married. They invite num_couples couples who are friends.
% Persons 1..P, P = 2*(num_couples+1): persons 2k-1 and 2k are a married couple.
% Hilary is person 1, Jocelyn is person 2.
:- lib(gfd).

model(Instance, Vars, [hil-Hil]) :-
    memberchk(num_couples-N, Instance),
    M is N + 1,
    P is 2*M,
    dim(H, [P, P]),
    % Each cell H[I,J] says whether person I and person J shake hands.
    ( multifor([I,J], 1, [P,P]), param(H) do
        H[I,J] :: 0..1
    ),

    % Nobody shakes hands with him or herself or with his or her spouse.
    % Shaking hands is mutual: H[I,J] = H[J,I].
    ( multifor([I,J], 1, [P,P]), param(H) do
        H[I,J] #= H[J,I],
        spouse(I, S),
        ( I =:= J -> H[I,J] #= 0 ; true ),
        ( J =:= S -> H[I,J] #= 0 ; true )
    ),

    % Each person has shaken hands with the people in his or her row.
    % Hands[I] is the number of hands person I has shaken.
    ( for(I, 1, P), foreach(Hand, Hands), param(H, P) do
        collection_to_list(H[I,1..P], Row),
        Hand #= sum(Row)
    ),

    % A person cannot shake hands with self or spouse, so at most P-2 hands.
    Hands = [Hil, _Jocelyn | Others],
    Hil :: 0..P-2,
    ( foreach(O, Others), param(P) do O :: 0..P-2 ),

    % All the answers are different. Jocelyn asks how many hands each person
    % has shaken, so the answers of the persons other than Jocelyn are all different.
    alldifferent([Hil | Others]),

    flatten_array(H, Cells),
    append(Hands, Cells, Vars).

% Hand counts first, then the handshakes they come from.
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

spouse(I, S) :-
    ( I mod 2 =:= 1 -> S is I + 1 ; S is I - 1 ).
