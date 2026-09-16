% Allergy logic puzzle: match each friend to a surname and an allergy.
% Friends are numbered Debra 0, Janet 1, Hugh 2, Rick 3.
friend(0..3).

% Each food and each surname belongs to exactly one friend, all different.
1 { eggs(F) : friend(F) } 1.
1 { mold(F) : friend(F) } 1.
1 { nuts(F) : friend(F) } 1.
1 { ragweed(F) : friend(F) } 1.
:- eggs(F), mold(F).
:- eggs(F), nuts(F).
:- eggs(F), ragweed(F).
:- mold(F), nuts(F).
:- mold(F), ragweed(F).
:- nuts(F), ragweed(F).

1 { baxter(F) : friend(F) } 1.
1 { lemon(F) : friend(F) } 1.
1 { malone(F) : friend(F) } 1.
1 { fleet(F) : friend(F) } 1.
:- baxter(F), lemon(F).
:- baxter(F), malone(F).
:- baxter(F), fleet(F).
:- lemon(F), malone(F).
:- lemon(F), fleet(F).
:- malone(F), fleet(F).

:- mold(3).                    % Rick is not allergic to mold
:- eggs(F), baxter(G), F != G. % Baxter is allergic to eggs
:- lemon(2).                   % Hugh is neither Lemon nor Fleet
:- fleet(2).
:- not ragweed(0).             % Debra is allergic to ragweed
:- lemon(1).                   % Janet is not Lemon, nor eggs, nor mold
:- eggs(1).
:- mold(1).

#show eggs/1.
#show mold/1.
#show nuts/1.
#show ragweed/1.
#show baxter/1.
#show lemon/1.
#show malone/1.
#show fleet/1.
