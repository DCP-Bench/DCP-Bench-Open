% Capital budgeting: choose among investments, each with a cash outflow now and a net present
% value (NPV), so that the total outflow stays within the budget and the total NPV is largest.
% Instance facts: budget(B); cash_flow(I, C): investment I needs C now; npv(I, V): it yields NPV V.
investment(I) :- npv(I,_).

% chosen(I): investment I is made.
{ chosen(I) } :- investment(I).

% The cash flows of all chosen investments must not exceed the budget.
:- budget(B), #sum { C,I : chosen(I), cash_flow(I,C) } > B.

% z is the total NPV of the chosen investments, which is to be maximised.
z(Z) :- Z = #sum { V,I : chosen(I), npv(I,V) }.
#maximize { Z : z(Z) }.

% x(I, true/false): whether investment I is chosen.
x(I,true) :- chosen(I).
x(I,false) :- investment(I), not chosen(I).

#show x/2.
#show z/1.
