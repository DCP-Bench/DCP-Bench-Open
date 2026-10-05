% Facility location: decide which of four candidate warehouses to open and how
% many units each ships to each region, meeting every region's demand at the
% least total cost (fixed cost of the open warehouses plus shipping cost),
% subject to three rules about which warehouses may be open together.
% Instance facts: warehouse_s(I, "City"): the city of warehouse I; fixed_costs(I, F);
% max_shipping(M); demands(J, D): the demand of region J; shipping_costs(I, J, C):
% the cost of shipping one unit from warehouse I to region J.
warehouse(I) :- fixed_costs(I,_).
region(J) :- demands(J,_).

% open(I): warehouse I is open.
{ open(I) } :- warehouse(I).

% ge(I,J,V): warehouse I ships at least V units to region J. A shipment is
% written in unary, up to max_shipping, so that the capacity, demand and cost
% sums below are propagated unit by unit; a choice of one value per shipment
% left the optimality proof unfinished after 180 s.
% A shipment with a positive unit cost never exceeds the region's demand in an
% optimal plan (the surplus could be dropped, see the implied constraints
% below), so its ladder stops at the smaller of max_shipping and the demand;
% a free shipment keeps the full range.
top(I,J,M) :- shipping_costs(I,J,0), max_shipping(M).
top(I,J,T) :- shipping_costs(I,J,C), C > 0, max_shipping(M), demands(J,D), T = (M + D - |M - D|) / 2.
{ ge(I,J,V) } :- warehouse(I), region(J), top(I,J,T), V = 1..T.
:- ge(I,J,V), V > 1, not ge(I,J,V-1).

% A warehouse sends at most max_shipping units in all, and nothing when it is closed.
:- warehouse(I), max_shipping(M), #count { J,V : ge(I,J,V) } > M.
:- ge(I,_,1), not open(I).

% Every region receives at least its demand.
:- demands(J,D), #count { I,V : ge(I,J,V) } < D.

% Implied by the two groups above: the open warehouses together can ship the
% total demand. Stated on the open warehouses so that it prunes before any
% shipment is chosen.
total_demand(S) :- S = #sum { D,J : demands(J,D) }.
:- total_demand(S), max_shipping(M), #sum { M,I : open(I) } < S.

% 1. If the New York warehouse is open, the Los Angeles one must be open too.
:- warehouse_s(NY,"New York"), warehouse_s(LA,"Los Angeles"), open(NY), not open(LA).
% 2. At most three warehouses are open.
:- #count { I : open(I) } > 3.
% 3. The Atlanta or the Los Angeles warehouse (or both) must be open.
:- warehouse_s(AT,"Atlanta"), warehouse_s(LA,"Los Angeles"), not open(AT), not open(LA).

% The total cost, which is minimised: the fixed cost of every open warehouse and
% the shipping cost of every unit shipped. It is stated on the unary atoms
% themselves, one term per unit.
#minimize { F,fixed,I : open(I), fixed_costs(I,F) ;
            C,ship,I,J,V : ge(I,J,V), shipping_costs(I,J,C) }.

% Implied constraints. Each one forbids a shipment plan that a one-unit change,
% keeping the same warehouses open, makes strictly cheaper while still meeting
% every demand and capacity. Such a plan is never optimal, so these remove no
% optimal answer; they only spare the solver from proving that by search.
% full(I): warehouse I already ships max_shipping units.
full(I) :- warehouse(I), max_shipping(M), #count { J,V : ge(I,J,V) } >= M.

% A region receiving more than its demand would be as well served with one unit
% less from a warehouse that charges for shipping to it.
:- ge(K,J,1), shipping_costs(K,J,C), C > 0, demands(J,D), #count { I,V : ge(I,J,V) } > D.

% A unit from I to J could come from another open warehouse K with spare
% capacity that ships to J more cheaply.
:- ge(I,J,1), open(K), K != I, not full(K),
   shipping_costs(I,J,A), shipping_costs(K,J,B), B < A.

% Two warehouses could swap one unit each between two regions more cheaply.
:- ge(I,J,1), ge(K,L,1), I < K, J != L,
   shipping_costs(I,J,A1), shipping_costs(K,L,A2), shipping_costs(I,L,B1), shipping_costs(K,J,B2),
   B1 + B2 < A1 + A2.

% Three warehouses could pass one unit each around three regions more cheaply:
% I's unit at J1 goes to J2, K's unit at J2 to J3, and L's unit at J3 to J1.
:- ge(I,J1,1), ge(K,J2,1), ge(L,J3,1), I != K, I != L, K != L, J1 != J2, J1 != J3, J2 != J3,
   shipping_costs(I,J1,A1), shipping_costs(K,J2,A2), shipping_costs(L,J3,A3),
   shipping_costs(I,J2,B1), shipping_costs(K,J3,B2), shipping_costs(L,J1,B3),
   B1 + B2 + B3 < A1 + A2 + A3.

% A unit from I to J could move to K, which in turn hands one of its units at
% region L to an open warehouse W with spare capacity, more cheaply.
:- ge(I,J,1), ge(K,L,1), open(W), not full(W), I != K, I != W, K != W, J != L,
   shipping_costs(I,J,A1), shipping_costs(K,L,A2), shipping_costs(K,J,B1), shipping_costs(W,L,B2),
   B1 + B2 < A1 + A2.

% The answer. total_cost lies in 0..10000, the range the problem declares, and
% is written in binary: bit(K) is bit K of the total, for K = 0..13 since
% 2^14 > 10000. The bits are tied to the costs by one sum. A sum assignment
% over the shipments would ground one atom for every possible total, and a
% choice of one of 10001 values gave the solver 10001 extra atoms to branch on.
% The tags keep the terms apart.
{ bit(K) : K = 0..13 }.
:- #sum { F,fixed,I : open(I), fixed_costs(I,F) ;
          C,ship,I,J,V : ge(I,J,V), shipping_costs(I,J,C) ;
          -(2**K),bit,K : bit(K) } != 0.
:- #sum { 2**K,K : bit(K) } > 10000.
% bits_sum(K,S): bits 0..K-1 add up to S; the total is the sum of all 14.
bits_sum(0,0).
bits_sum(K+1,S + 2**K) :- bits_sum(K,S), K < 14, bit(K).
bits_sum(K+1,S) :- bits_sum(K,S), K < 14, not bit(K).
total_cost(T) :- bits_sum(14,T).

% open_warehouse(I, 1) when warehouse I is open, open_warehouse(I, 0) when it is not.
open_warehouse(I,1) :- open(I).
open_warehouse(I,0) :- warehouse(I), not open(I).

% ships(I, J, N): warehouse I sends N units to region J, including 0.
ships(I,J,N) :- ge(I,J,N), not ge(I,J,N+1).
ships(I,J,0) :- warehouse(I), region(J), not ge(I,J,1).

#show total_cost/1.
#show open_warehouse/2.
#show ships/3.
