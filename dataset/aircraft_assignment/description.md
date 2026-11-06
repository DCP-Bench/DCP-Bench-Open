This problem involves assigning multiple types of aircraft to a set of routes to minimize the total operational cost.
Each aircraft type has a limited number of available units. Each route has a specific passenger demand that must be satisfied.
For each aircraft type and route, we are given the passenger capacity and the operational cost.
The goal is to determine how many aircraft of each type to assign to each route to meet all passenger demands, stay within the availability limits for each aircraft type, and minimize the overall cost.

Print the allocation matrix (allocation) as a list of lists of integers; allocation[i][j] represents the number of aircraft of type i assigned to route j.
