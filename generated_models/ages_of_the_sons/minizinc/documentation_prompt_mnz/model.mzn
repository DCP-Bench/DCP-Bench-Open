include "globals.mzn";

% The product of the ages is 36
int: product = 36;

% We want to find three ages A1, A2, A3 such that:
% - A1 >= A2 >= A3 (to order from oldest to youngest)
% - A1 * A2 * A3 = 36
% - The sum of ages equals the number of windows in the building (unknown)
% - The oldest son is unique (there is a single oldest son)

% Define the domain for ages: since product is 36, max age can be 36
var 1..36: A1;
var 1..36: A2;
var 1..36: A3;

% Order the ages descending
constraint A1 >= A2 /\ A2 >= A3;

% Product constraint
constraint A1 * A2 * A3 = product;

% The sum of ages (unknown number of windows)
var 3..108: sum_ages = A1 + A2 + A3;

% The mathematician needed more info after knowing the sum,
% so the sum must not uniquely identify the ages.
% That means there must be at least two different triples with the same sum and product=36.

% We will find all triples with product=36 and order descending
% Then find sums that correspond to more than one triple.

% To model this, we enumerate all possible triples with product=36 and order descending
% and find sums with multiple triples.

% We create an array of all possible triples with product=36 and order descending
% and store their sums.

% Since Minizinc does not support dynamic arrays easily, we do this by a predicate and search.

% We will solve for all solutions and filter sums with multiple triples externally.

% To enforce uniqueness of oldest son, the oldest age must be unique (no tie)
% So A1 > A2

constraint A1 > A2;

solve satisfy;

output [
    "{",
    "\"A1\": ", show(A1), ",",
    "\"A2\": ", show(A2), ",",
    "\"A3\": ", show(A3),
    "}"
];