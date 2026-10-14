% Dinner: a family goes out to dinner with 1-6 grandparents, 1-10 parents and 1-40 children.
% Grandparents cost $3, parents $2 and children $0.50; 20 people in total must pay $20 in total.
% The numbers belong to the problem statement, not to an instance (there is no instance data).

% "taking 1-6 grandparents, 1-10 parents and/or 1-40 children"
1 { grandparents(N) : N = 1..6 } 1.
1 { parents(N) : N = 1..10 } 1.
1 { children(N) : N = 1..40 } 1.

% "There must be 20 total people at dinner"
:- not 20 = #sum { N,g : grandparents(N); N,p : parents(N); N,c : children(N) }.

% "... and it must cost $20". A child costs $0.50, so the prices are counted in half dollars:
% a grandparent costs 6, a parent 4, a child 1, and the dinner costs 40.
:- not 40 = #sum { 6*N,g : grandparents(N); 4*N,p : parents(N); N,c : children(N) }.

#show grandparents/1.
#show parents/1.
#show children/1.
