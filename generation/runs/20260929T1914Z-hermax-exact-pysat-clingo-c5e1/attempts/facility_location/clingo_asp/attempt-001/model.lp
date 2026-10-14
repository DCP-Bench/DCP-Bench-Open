% Facility location: decide which of four candidate warehouses to open and how
% many units each ships to each region, meeting every region's demand at the
% least total cost (fixed cost of the open warehouses plus shipping cost),
% subject to three rules about which warehouses may be open together.
% warehouse_s(I, "City"): the city of warehouse I; fixed_costs(I, F); max_shipping(M);
% demands(J, D): the demand of region J; shipping_costs(I, J, C): the cost per unit.
warehouse(I) :- fixed_costs(I,_).
region(J) :- demands(J,_).

% open_warehouse(I, 1) when warehouse I is open, open_warehouse(I, 0) when it is not.
1 { open_warehouse(I,B) : B = 0..1 } 1 :- warehouse(I).
% ships(I, J, N): warehouse I sends N units to region J.
1 { ships(I,J,N) : N = 0..M } 1 :- warehouse(I), region(J), max_shipping(M).

% A warehouse sends at most max_shipping units, and nothing when it is closed.
:- open_warehouse(I,B), max_shipping(M), #sum { N,J : ships(I,J,N) } > M * B.

% Every region receives at least its demand.
:- demands(J,D), D > #sum { N,I : ships(I,J,N) }.

% 1. If the New York warehouse is open, the Los Angeles one must be open too.
:- warehouse_s(NY,"New York"), warehouse_s(LA,"Los Angeles"), open_warehouse(NY,1), open_warehouse(LA,0).
% 2. At most three warehouses are open.
:- #count { I : open_warehouse(I,1) } > 3.
% 3. The Atlanta or the Los Angeles warehouse (or both) must be open.
:- warehouse_s(AT,"Atlanta"), warehouse_s(LA,"Los Angeles"), open_warehouse(AT,0), open_warehouse(LA,0).

% Total cost = fixed costs of the open warehouses + cost of everything shipped.
total_cost(T) :- T = #sum { F * B,I : open_warehouse(I,B), fixed_costs(I,F) ;
                            C * N,I,J : ships(I,J,N), shipping_costs(I,J,C) }.
#minimize { T : total_cost(T) }.

#show total_cost/1.
#show open_warehouse/2.
#show ships/3.
