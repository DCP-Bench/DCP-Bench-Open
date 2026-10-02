:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Finding celebrities: at a party, a celebrity is a guest that everybody knows
% and that knows only celebrities. Decide who the celebrities are, with at
% least one celebrity present.
model(Instance, Vars, [celebrities-Celebrities]) :-
    Graph = Instance.graph,    % Graph[i][j] = 1 when guest i knows guest j

    % Celebrities[i] is 1 when guest i is a celebrity
    length(Graph, N),
    length(Celebrities, N),
    Celebrities ins 0..1,

    % the number of celebrities, at least one
    NumCelebrities in 1..N,
    sum(Celebrities, #=, NumCelebrities),

    % a guest is a celebrity exactly when all N guests know him or her and he or
    % she knows exactly as many guests as there are celebrities (the celebrities
    % themselves, as everybody knows them)
    transpose(Graph, KnownBy),
    maplist({N, NumCelebrities}/[Celebrity, KnownByRow, KnowsRow]>>(
                sum_list(KnownByRow, KnownByCount),
                sum_list(KnowsRow, KnowsCount),
                Celebrity #<==> ((KnownByCount #= N) #/\ (KnowsCount #= NumCelebrities))),
            Celebrities, KnownBy, Graph),
    append(Celebrities, [NumCelebrities], Vars).
