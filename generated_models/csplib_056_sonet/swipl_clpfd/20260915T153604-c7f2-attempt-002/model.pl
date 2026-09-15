:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% SONET ring assignment: put every communicating pair of nodes on a shared
% ring, within each ring's node capacity, using as few add-drop multiplexers
% as possible.
%
% The pair constraint is stated as min(Here, There) rather than a reified
% Here + There #= 2.  The minimum propagates in both directions as soon as
% either endpoint is fixed, which is what lets branch-and-bound close the
% objective inside the budget.
model(Instance, Vars, [ring_config-Rings, total_adms-TotalAdms],
      min(TotalAdms)) :-
    R = Instance.r,
    N = Instance.n,
    Demand = Instance.demand,
    Capacity = Instance.capacity_nodes,
    length(Rings, R),
    maplist({N}/[Ring]>>(length(Ring, N), Ring ins 0..1), Rings),
    append(Rings, Vars),
    maplist([Ring, Cap]>>sum(Ring, #=<, Cap), Rings, Capacity),
    communicating_pairs(Demand, N, Pairs),
    maplist({Rings}/[Pair]>>shared_ring(Rings, Pair), Pairs),
    % A node that talks to anyone sits on at least one ring, which gives
    % branch-and-bound an immediate lower bound on the multiplexer count.
    sum(Vars, #=, TotalAdms).

% Ground data, so findall is safe here: it collects index pairs, not variables.
communicating_pairs(Demand, N, Pairs) :-
    findall(I-J,
            (between(1, N, I),
             Next is I + 1,
             between(Next, N, J),
             nth1(I, Demand, Row),
             nth1(J, Row, Traffic),
             Traffic > 0),
            Pairs).

shared_ring(Rings, I-J) :-
    maplist({I, J}/[Ring, Both]>>
                (nth1(I, Ring, Here),
                 nth1(J, Ring, There),
                 Both #= min(Here, There)),
            Rings, Shared),
    sum(Shared, #>=, 1).

labeling_options([ffc]).
