% Template design: a printing firm prints several variations of a product on mother sheets, each
% printed from a template with a fixed number of slots. Decide how many sheets to print from each
% template and how many copies of each variation to put on each template, so that every variation's
% demand is met and the total number of printed sheets is smallest.
% Instance facts: n_slots(S): slots on a template; n_templates(T); n_var(V): number of variations;
% demand(I,D): demand for variation I.
template(0..T-1) :- n_templates(T).
variation(0..V-1) :- n_var(V).
top(M) :- M = #max { D : demand(_,D) }.
total_demand(S) :- S = #sum { D,I : demand(I,D) }.

% Sheets printed from a template: between 1 and the largest demand (the reference's upper bound).
% Order encoding: printed_ge(T,P) holds when template T is printed P times or more, P >= 2.
{ printed_ge(T,P) : P = 2..M } :- template(T), top(M).
:- printed_ge(T,P+1), not printed_ge(T,P), P >= 2.

% production(T,P): template T is printed exactly P times.
production(T,1) :- template(T), not printed_ge(T,2).
production(T,P) :- printed_ge(T,P), not printed_ge(T,P+1).

% layout(T,I,K): template T carries K copies of variation I, between 0 and the number of
% variations (the reference's domain).
1 { layout(T,I,K) : K = 0..V } 1 :- template(T), variation(I), n_var(V).

% All slots of a template are populated.
:- template(T), n_slots(S), #sum { K,I : layout(T,I,K) } != S.

% items_ge(T,I,X) holds when the sheets of template T carry X items of variation I or more, X up
% to the demand for I (more than the demand is never needed). A template with K copies printed P
% times carries K*P items, so it carries X items or more when P >= ceil(X/K): the first K items are
% on the first sheet, and each further item needs the matching number of sheets. Counting these
% threshold atoms gives each product as a count the solver can reason about, instead of a product of two unknowns.
items_ge(T,I,X) :- layout(T,I,K), demand(I,D), X = 1..K, X <= D.
items_ge(T,I,X) :- layout(T,I,K), K >= 1, demand(I,D), X = K+1..D, printed_ge(T,(X+K-1)/K).

% The demand for every variation is met: the items of the variation, added over all templates, reach the demand.
:- demand(I,D), #count { T,X : items_ge(T,I,X) } < D.

% Implied constraint from the reference: every template fills all its slots, so the sheets together
% must carry at least the total demand, n_slots * sheets >= total demand.
:- n_slots(S), total_demand(DT), #sum { S,T : template(T) ; S,T,P : printed_ge(T,P) } < DT.

% Minimise the number of printed sheets (every template has its first sheet, so count the extra ones).
#minimize { 1,T,P : printed_ge(T,P) }.

#show production/2.
#show layout/3.
