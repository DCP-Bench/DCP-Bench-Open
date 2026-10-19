% Who killed Agatha?
% Persons are the instance's names in order: 1 Agatha herself, 2 the butler, 3 Charles
% (1-based inside the model; the output is 0-based).
% Hate H[I,J]: person I hates person J. Wealth W[I] is a rank, equal ranks allowed,
% so "richer" is the strict comparison of ranks.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [killer-Killer], none) :-
    memberchk(names-Names, Instance),
    length(Names, N),
    NN1 is N - 1,
    dim(H, [N, N]),
    H[1..N, 1..N] :: 0..1,
    dim(W, [N]),
    W[1..N] :: 0..NN1,
    Killer :: 0..NN1,

    % A killer always hates, and is no richer than his victim (the victim is Agatha).
    ( for(P, 1, N), param(Killer, H, W) do
        ( (Killer #= P - 1) =>
            ( (H[P, 1] #= 1) and (W[P] #=< W[1]) ) )
    ),

    % Charles hates noone that Agatha hates.
    ( for(J, 1, N), param(H) do
        ( (H[1, J] #= 1) => (H[3, J] #= 0) )
    ),

    % Agatha hates everybody except the butler.
    ( for(J, 1, N), param(H) do
        ( J =:= 2 -> H[1, J] #= 0 ; H[1, J] #= 1 )
    ),

    % The butler hates everyone not richer than Aunt Agatha.
    ( for(J, 1, N), param(H, W) do
        ( (W[J] #=< W[1]) => (H[2, J] #= 1) )
    ),

    % The butler hates everyone whom Agatha hates.
    ( for(J, 1, N), param(H) do
        ( (H[1, J] #= 1) => (H[2, J] #= 1) )
    ),

    % Noone hates everyone.
    ( for(I, 1, N), param(H, N) do
        ( collection_to_list(H[I, 1..N], Row),
          sum(Row) #< N )
    ),

    flatten_array(H, HF),
    flatten_array(W, WF),
    append([Killer | WF], HF, Vars).
