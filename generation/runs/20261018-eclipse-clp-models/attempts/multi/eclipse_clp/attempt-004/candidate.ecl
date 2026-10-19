% Multi-commodity transportation problem.
% Origins ship products to destinations. Each origin i has a supply of each
% product p, each destination j has a demand for each product p, and each lane
% (i, j) has a limit on the total shipped over all products. The cost of
% shipping one unit of product p from origin i to destination j is
% ShippingCost(i, j, p). Minimise the total cost of shipping all products.

:- lib(gfd).
:- lib(listut).

model(Instance, Vars, [total_cost-Total], min(Total)) :-
    memberchk(supply-Supply, Instance),
    memberchk(demand-Demand, Instance),
    memberchk(limit-Limit, Instance),
    memberchk(cost-Cost, Instance),
    length(Supply, NO),
    length(Demand, ND),
    Supply = [Row1|_],
    length(Row1, NP),
    dim(X, [NO, ND, NP]),
    flatten_array(X, Vars),

    % Quantity shipped of product p from origin i to destination j, bounded by
    % the smallest of the origin supply, the destination demand and the lane limit.
    ( multifor([I,J,P], 1, [NO,ND,NP]),
      param(X, Supply, Demand, Limit) do
        nth1(I, Supply, SR), nth1(P, SR, S),
        nth1(J, Demand, DR), nth1(P, DR, D),
        nth1(I, Limit, LR), nth1(J, LR, L),
        Ub is min(S, min(D, L)),
        X[I,J,P] :: 0..Ub
    ),

    % Each origin i has a certain supply of each product p: it ships at most that much.
    ( multifor([I,P], 1, [NO,NP]),
      param(X, Supply, ND) do
        nth1(I, Supply, SR), nth1(P, SR, S),
        ( for(J,1,ND), foreach(V,Vs), param(X,I,P) do
            V = X[I,J,P]
        ),
        sum(Vs) #=< S
    ),

    % Each destination j has a certain demand for each product p: it receives exactly that much.
    ( multifor([J,P], 1, [ND,NP]),
      param(X, Demand, NO) do
        nth1(J, Demand, DR), nth1(P, DR, D),
        ( for(I,1,NO), foreach(V,Vs), param(X,J,P) do
            V = X[I,J,P]
        ),
        sum(Vs) #= D
    ),

    % Each lane from origin i to destination j has a limit on the total shipped over all products.
    ( multifor([I,J], 1, [NO,ND]),
      param(X, Limit, NP) do
        nth1(I, Limit, LR), nth1(J, LR, L),
        ( for(P,1,NP), foreach(V,Vs), param(X,I,J) do
            V = X[I,J,P]
        ),
        sum(Vs) #=< L
    ),

    % The cost of shipping one unit of product p from origin i to destination j is ShippingCost(i, j, p).
    % The problem aims to minimise the total cost of shipping all products.
    ( multifor([I,J,P], 1, [NO,ND,NP]), foreach(T, Terms),
      param(X, Cost) do
        nth1(I, Cost, CI), nth1(J, CI, CIJ), nth1(P, CIJ, C),
        T #= C * X[I,J,P]
    ),
    Total #= sum(Terms).
