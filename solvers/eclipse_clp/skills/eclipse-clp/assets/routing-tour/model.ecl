% Shortest tour through 6 cities. Next[I] is the city visited after city I.
% circuit/1 (library ic) forces one cycle through all cities;
% element/3 reads the distance of the chosen arc from row I of the matrix.
:- lib(ic).
:- lib(branch_and_bound).
:- lib(listut).

dist([[0, 7, 9, 8, 20, 12],
      [7, 0, 10, 4, 11, 14],
      [9, 10, 0, 15, 5, 6],
      [8, 4, 15, 0, 17, 9],
      [20, 11, 5, 17, 0, 10],
      [12, 14, 6, 9, 10, 0]]).

main :-
    dist(Rows),
    length(Rows, N),
    length(Next, N),
    Next :: 1..N,
    circuit(Next),                           % a single cycle through all cities
    ( for(I, 1, N), foreach(Nx, Next), foreach(Row, Rows), foreach(D, Ds) do
        Nx #\= I,                            % no self loop
        element(Nx, Row, D)                  % D = Row[Nx], 1-based
    ),
    Cost #= sum(Ds),
    bb_min(search(Next, 0, first_fail, indomain_min, complete, []), Cost,
           bb_options{report_success:true/0, report_failure:true/0}),
    printf("Tour length: %d%n", [Cost]),
    % follow the successors from city 1
    follow(1, Next, N, Tour),
    printf("Tour: %w%n", [Tour]).

follow(_, _, 0, []) :- !.
follow(City, Next, K, [City|Rest]) :-
    nth1(City, Next, Succ),                  % nth1/3 lives in lib(listut)
    K1 is K - 1,
    follow(Succ, Next, K1, Rest).
