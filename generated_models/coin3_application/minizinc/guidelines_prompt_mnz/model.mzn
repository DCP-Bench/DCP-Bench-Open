
% Include necessary library for global constraints (not strictly needed here but good practice)
include "globals.mzn";

% Data
int: num_den = 6;
array[1..num_den] of int: den = [1,2,5,10,20,50];
int: max_amount = 99;

% Decision variables: how many coins of each denomination
array[1..num_den] of var 0..max_amount: x;

% Auxiliary vars: for each amount a, how many coins of each denom we use to pay exactly a
array[1..max_amount, 1..num_den] of var 0..max_amount: y;

% Ensure that for every amount from 1 to 99 we can pay exactly that amount
constraint
  forall(a in 1..max_amount) (
    % sum of denominations times counts equals the amount
    sum(i in 1..num_den)( y[a,i] * den[i] ) = a
    /\
    % cannot use more coins of a type than we have
    forall(i in 1..num_den)( y[a,i] <= x[i] )
  );

% Objective: minimize total number of coins
var 0..max_amount * num_den: total_coins = sum(i in 1..num_den)( x[i] );

solve minimize total_coins;

% Output the list x in JSON format
output [
  "{",
    "\"x\": [" ++ join(",", [show(x[i]) | i in 1..num_den]) ++ "]",
  "}"
];
