% Social golfers: schedule the golfers of a club, in groups of equal size each week, for a number
% of weeks so that no two golfers play in the same group on more than one occasion.
% Instance facts: n_weeks(W), n_groups(G), group_size(S); there are G * S golfers, numbered from 0.
golfer(0..G*S-1) :- n_groups(G), group_size(S).
week(0..W-1) :- n_weeks(W).
group(0..G-1) :- n_groups(G).

% assign(I, W, G): golfer I plays in group G in week W. Every golfer plays in exactly one group
% each week.
1 { assign(I,W,G) : group(G) } 1 :- golfer(I), week(W).

% Each group has exactly group_size players in every week.
:- group(G), week(W), group_size(S), S != #count { I : assign(I,W,G) }.

% Each pair of golfers meets at most once: they share a group in at most one week.
:- golfer(I1), golfer(I2), I1 < I2, #count { W : assign(I1,W,G), assign(I2,W,G) } >= 2.

#show assign/3.
