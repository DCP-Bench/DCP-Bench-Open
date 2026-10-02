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
% Unary threshold atoms keep the demand sums below easy to propagate.
{ printed_ge(T,P) : P = 2..M } :- template(T), top(M).
:- printed_ge(T,P+1), not printed_ge(T,P), P >= 2.

% production(T,P): template T is printed exactly P times.
production(T,1) :- template(T), not printed_ge(T,2).
production(T,P) :- printed_ge(T,P), not printed_ge(T,P+1).

% layout(T,I,K): template T carries K copies of variation I, between 0 and the number of
% variations (the reference's domain).
1 { layout(T,I,K) : K = 0..V } 1 :- template(T), variation(I), n_var(V).

% copies_ge(T,I,K) holds when template T carries K copies of variation I or more, K >= 1.
copies_ge(T,I,K) :- layout(T,I,K2), K = 1..K2.

% All slots of a template are populated.
:- template(T), n_slots(S), #sum { K,I : layout(T,I,K) } != S.

% The demand for every variation is met: the sheets of each template times the copies of the variation
% on it, added over templates, must reach the demand. A template printed P times with K copies
% gives K*P items: K for the first sheet, plus one for each pair of a copy (copies_ge) and a sheet
% beyond the first (printed_ge), which is what the second element counts.
:- demand(I,D), #sum { 1,T,K : copies_ge(T,I,K) ; 1,T,K,P : copies_ge(T,I,K), printed_ge(T,P) } < D.

% Implied constraint from the reference: every template fills all its slots, so the sheets together
% must carry at least the total demand, n_slots * sheets >= total demand.
:- n_slots(S), total_demand(DT), #sum { S,T : template(T) ; S,T,P : printed_ge(T,P) } < DT.

% Minimise the number of printed sheets (every template has its first sheet, so count the extra ones).
#minimize { 1,T,P : printed_ge(T,P) }.

#show production/2.
#show layout/3.
