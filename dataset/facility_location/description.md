A company is considering opening warehouses in four cities to meet regional demands at minimal costs. The potential
cities for these warehouses are New York, Los Angeles, Chicago, and Atlanta. Each open warehouse has a fixed weekly cost
and can ship at most `max_shipping` units per week, and a closed one ships nothing. Shipping one unit from a warehouse to
a region has a given cost, and each region must receive at least its weekly demand.

The company needs to decide which warehouses to open based on several constraints:

1. If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
2. No more than three warehouses can be operational in any given week.
3. Either the Atlanta or the Los Angeles warehouse must be opened.

The objective is to determine the optimal set of warehouses to open and the distribution of shipments to various regions
to minimize total costs: the fixed costs of the open warehouses plus the shipping costs.

Print the total cost (total_cost) as an integer, whether the warehouses are open (open_warehouse) as a list of booleans, and the shipping details for each
region per warehouse (ships) as a list of lists where ships[i][j] indicates the number of units shipped from warehouse i to region j - including the non-opened warehouses as 0s.
