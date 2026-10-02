% Grocery: a kid buys several items. The cashier's total in cents is the sum of the item prices and
% also their product (the product of the prices in euros is the total in euros, so in cents the product
% of the prices equals total_price * 100^(items-1)). Find the item prices in cents.
% Instance facts: total_price(T); num_items(N).
item(0..N-1) :- num_items(N).

% The product of the prices must be total_price * 100^(items-1). Clingo integers are 32 bits, so
% this model only fits instances where that number is below 2^31 (it is 7.2e8 at most here).
product_target(P) :- total_price(T), num_items(N), P = T * 100 ** (N-1).

% Every price divides the product, since all prices are whole numbers. Only those values are
% possible prices, between 1 and total_price (the reference's domain).
price_value(X) :- total_price(T), product_target(P), X = 1..T, P \ X == 0.

% prices(I,X): item I costs X cents.
1 { prices(I,X) : price_value(X) } 1 :- item(I).

% The prices of all items add up to the total price.
:- total_price(T), #sum { X,I : prices(I,X) } != T.

% The product is built item by item, keeping only partial products that still divide the target
% (a partial product of the final product must divide it). The check Q <= P/X first avoids
% overflowing the 32-bit integers when multiplying Q by X.
reach(1).
small(Q,X) :- reach(Q), price_value(X), product_target(P), Q <= P/X.
step(Q,X,Q*X) :- small(Q,X), product_target(P), P \ (Q*X) == 0.
reach(R) :- step(_,_,R).

% prefix(I,Q): the first I items have the product Q.
prefix(0,1).
prefix(I+1,R) :- prefix(I,Q), prices(I,X), step(Q,X,R).

% The product of all prices is the target.
:- num_items(N), product_target(P), not prefix(N,P).

#show prices/2.
