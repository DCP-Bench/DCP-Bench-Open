% Handshaking: Hilary and Jocelyn (a married couple) invite some couples to
% dinner. When they arrive people shake hands; nobody shakes hands with himself
% or herself or with his or her spouse. Jocelyn then asks everybody how many
% hands they have shaken and all the answers are different. How many hands has
% Hilary shaken?

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

% all answers are different, except that Hilary does not count (she is the
% one whose answer is wanted)
constraint forall(i, j in Persons where 1 <= i /\ i < j) (x[i] != x[j]);

% nobody shakes hands with his or her spouse
constraint forall(c in 0..n div 2 - 1)
    (not y[2 * c, 2 * c + 1] /\ not y[2 * c + 1, 2 * c]);

% nobody shakes hands with himself or herself, and x[i] counts person i's handshakes
constraint forall(i in Persons) (not y[i, i]);
constraint forall(i in Persons) (x[i] = sum(j in Persons) (bool2int(y[i, j])));

% handshaking is symmetric: i shakes hands with j exactly when j shakes hands with i
constraint forall(i, j in Persons where i < j) (y[i, j] = y[j, i]);

solve satisfy;

output ["{\"hil\": ", show(hil), "}"];
