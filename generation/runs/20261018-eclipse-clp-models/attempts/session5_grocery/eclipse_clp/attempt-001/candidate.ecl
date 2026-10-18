% Session 5 grocery: a kid buys a number of items (num_items). The cashier
% first multiplies the item prices and then adds them; both give the same
% total price (total_price). Find the prices of the items, in cents.

:- lib(ic).

model(Instance, Prices, [prices-Prices]) :-
    memberchk(num_items-N, Instance),
    memberchk(total_price-T, Instance),
    length(Prices, N),
    Prices :: 1..T,

    % The prices, added together, give the total price.
    sum(Prices) #= T,

    % The prices, multiplied together, give the total price. Prices are in
    % cents, so the product of N prices is in cents^N; dividing by 100^(N-1)
    % brings it back to cents, which is the total price.
    Scale is 100^(N-1),
    Product is T * Scale,
    ( foreach(P, Prices), fromto(1, A, B, Prod), param(Product) do
        B :: 1..Product,
        B #= A * P
    ),
    Prod #= Product.
