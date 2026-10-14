% Covering: hire workers at the lowest total cost so that every task has at least one hired
% worker who is qualified for it.
% Instance facts: nb_workers(W), num_tasks(T); cost(I, C): hiring worker I costs C (the field
% Cost lowered to cost); qualified(J, K, W): the K-th worker qualified for task J is worker W,
% numbered from 1 (the field Qualified lowered to qualified); worker I of the output has number I + 1.
worker(0..W-1) :- nb_workers(W).
task(0..T-1) :- num_tasks(T).

% hired(I): worker I is hired.
{ hired(I) } :- worker(I).

% Every task needs a hired worker who is qualified for it.
covered(J) :- qualified(J,_,Q), hired(Q - 1).
:- task(J), not covered(J).

% The total cost of hiring, to be minimised.
total_cost(S) :- S = #sum { K,I : hired(I), cost(I,K) }.
#minimize { S : total_cost(S) }.

% workers(I, true/false): whether worker I is hired.
workers(I,true) :- hired(I).
workers(I,false) :- worker(I), not hired(I).

#show total_cost/1.
#show workers/2.
