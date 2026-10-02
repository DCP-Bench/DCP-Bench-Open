% Handshaking: Hilary and Jocelyn (a married couple) invite some couples to
% dinner. When they arrive people shake hands; nobody shakes hands with himself
% or herself or with his or her spouse. Jocelyn then asks everybody how many
% hands they have shaken and all the answers are different. How many hands has
% Hilary shaken?
include "globals.mzn";

int: num_couples;  % invited couples, not counting Hilary and Jocelyn

% persons 0..n-1 are coded as couples (0,1), (2,3), ...; person 0 is Hilary
% and person 1 is her spouse Jocelyn
int: n = 2 + num_couples * 2;
set of int: Persons = 0..n - 1;

% x[i] = number of hands person i has shaken; at most n-2 since nobody shakes
% their own or their spouse's hand
array[Persons] of var 0..n - 2: x;

% y[i, j] = person i shakes hands with person j
array[Persons, Persons] of var bool: y;

% Hilary's number of handshakes, the quantity asked for
var 0..n - 2: hil = x[0];

% all answers are different, except that Hilary's does not count (hers is the
% one that is asked for)
constraint all_different([x[i] | i in 1..n - 1]);

% nobody shakes hands with his or her spouse
constraint forall(c in 0..n div 2 - 1)
    (not y[2 * c, 2 * c + 1] /\ not y[2 * c + 1, 2 * c]);

% nobody shakes hands with himself or herself, and x[i] counts person i's handshakes
constraint forall(i in Persons) (not y[i, i]);
constraint forall(i in Persons) (x[i] = sum(j in Persons) (bool2int(y[i, j])));

% handshaking is symmetric: i shakes hands with j exactly when j shakes hands with i
constraint forall(i, j in Persons where i < j) (y[i, j] = y[j, i]);

% Symmetry between the invited couples (not between Hilary and Jocelyn, whose
% answer is asked for). Exchanging the two spouses of an invited couple, or
% exchanging two invited couples, gives the same situation under other names and
% the same number of hands for Hilary. Only one naming of each situation is kept:
% the answers of a couple are in increasing order, and the couples are in
% increasing order of their first spouse's answer. Without this the number of
% solutions (8! * 2^8 for 8 couples) is far too large to enumerate, while the
% value of hil is the same in all of them.
constraint forall(c in 1..num_couples) (x[2 * c] < x[2 * c + 1]);
constraint forall(c in 1..num_couples - 1) (x[2 * c] < x[2 * c + 2]);

solve satisfy;

output ["{\"hil\": ", show(hil), "}"];
