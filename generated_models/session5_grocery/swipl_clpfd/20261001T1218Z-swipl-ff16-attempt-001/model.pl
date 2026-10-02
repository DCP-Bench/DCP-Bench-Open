:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Grocery: a kid buys some items. The cashier multiplied the prices instead of
% adding them, and the product came out the same as the sum, the total price.
% Prices are in cents, so a product of n prices in euros is the product in
% cents divided by 100^n; it equals the total price in euros when the product
% in cents is the total price in cents times 100^(n-1). What were the prices?
model(Instance, Prices, [prices-Prices]) :-
    Total = Instance.total_price,           % total price in cents
    NumItems = Instance.num_items,

    % Prices[i] is the price of item i in cents, between 1 and the total.
    length(Prices, NumItems),
    Prices ins 1..Total,

    % the prices add up to the total price
    sum(Prices, #=, Total),

    % the product of the prices, in cents, is the total price scaled by 100
    % for each multiplication
    Product is Total * 100 ^ (NumItems - 1),
    foldl([Price, Product0, Product1]>>(Product1 #= Product0 * Price), Prices, 1, Product),

    % Implied domain: every price divides the product, so only the divisors of
    % the product are tried. This keeps the search from testing each price up
    % to the total.
    findall(Divisor, (between(1, Total, Divisor), Product mod Divisor =:= 0), Divisors),
    list_to_domain(Divisors, Domain),
    Prices ins Domain,

    % Symmetry breaking (not part of the problem statement): the items can be
    % listed in any order, so the prices are given in non-decreasing order.
    chain(Prices, #=<).

% list_to_domain(+Ints, -Domain): the finite domain holding exactly Ints.
list_to_domain([First|Rest], Domain) :-
    foldl([X, Domain0, Domain1]>>(Domain1 = Domain0 \/ X), Rest, First, Domain).

% Search the prices from the lowest item up.
labeling_options([leftmost]).
