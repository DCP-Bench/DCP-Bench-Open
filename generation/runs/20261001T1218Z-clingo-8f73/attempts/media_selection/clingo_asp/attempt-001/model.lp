% Media selection: choose advertising media so that every target audience is reached by at least
% one chosen medium, at the smallest total cost. An audience may be covered more than once.
% Instance facts: target_audiences(T, _) numbers the audiences and advertising_media(M, _) the media,
% incidence_matrix(T, M, W): W is 1 when medium M reaches audience T, and 0 otherwise,
% media_costs(M, C): the cost of medium M.
audience(T) :- target_audiences(T,_).
medium(M) :- advertising_media(M,_).

% chosen(M): medium M is selected.
{ chosen(M) : medium(M) }.

% Every audience is covered by at least one selected medium.
:- audience(T), #sum { W,M : chosen(M), incidence_matrix(T,M,W) } < 1.

% min_total_cost: the total cost of the selected media, which is to be minimised.
min_total_cost(S) :- S = #sum { C,M : chosen(M), media_costs(M,C) }.
#minimize { S : min_total_cost(S) }.

% is_selected(M, true/false): whether medium M is selected.
is_selected(M,true) :- chosen(M).
is_selected(M,false) :- medium(M), not chosen(M).

#show is_selected/2.
#show min_total_cost/1.
