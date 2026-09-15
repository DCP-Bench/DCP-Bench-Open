:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Movie scheduling: watch as many films as possible without two of them
% overlapping in time.
model(Instance, Selected, [selected_movies-Selected], max(Watched)) :-
    Movies = Instance.movies,
    length(Movies, NumMovies),
    length(Selected, NumMovies),
    Selected ins 0..1,
    % Each movie row is title, start, end, so the times are read positionally.
    maplist([Movie, Start-End]>>(nth0(1, Movie, Start), nth0(2, Movie, End)),
            Movies, Times),
    Last is NumMovies - 1,
    numlist(0, Last, Indices),
    maplist({Selected, Times, Last}/[I]>>
                no_clash(Selected, Times, Last, I),
            Indices),
    sum(Selected, #=, Watched).

no_clash(Selected, Times, Last, I) :-
    Next is I + 1,
    (   Next > Last
    ->  true
    ;   numlist(Next, Last, Others),
        nth0(I, Times, StartI-EndI),
        nth0(I, Selected, Here),
        maplist({Selected, Times, Here, StartI, EndI}/[J]>>
                    exclusive(Selected, Times, Here, StartI, EndI, J),
                Others)
    ).

% Two movies whose intervals overlap cannot both be watched.
exclusive(Selected, Times, Here, StartI, EndI, J) :-
    nth0(J, Times, StartJ-EndJ),
    (   EndI > StartJ, EndJ > StartI
    ->  nth0(J, Selected, There),
        Here + There #=< 1
    ;   true
    ).
