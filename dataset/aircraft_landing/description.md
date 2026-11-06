The Aircraft Landing Problem involves scheduling the landing of a set of aircraft on a single runway.
Each aircraft has a specified time window (earliest and latest possible landing time) and a target landing time.
Penalties are incurred for landing earlier or later than the target time. Additionally, a minimum separation time between the landings of any two aircraft must be respected.
This specific problem instance assumes a fixed landing sequence for the aircraft.
The objective is to determine the exact landing time for each aircraft to minimize the total penalty, while respecting all time windows and separation constraints.

Print the landing time for each aircraft (landing_times) as a list of integers, and the minimized total penalty (total_penalty) as an integer.
