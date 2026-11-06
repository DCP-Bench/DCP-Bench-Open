Progress City is considering a mass-transit bus system to reduce in-city driving. The goal is to determine the minimum
number of buses required to meet the transportation needs throughout the day. The demand for buses is approximated as
constant over successive 4-hour intervals. Each bus can operate only 8 successive hours a day, so a bus that starts
in one interval also works in the next one. The day is cyclic: the first interval follows the last.

We need to ensure that the number of buses available in each 4-hour interval, those starting in it and those that started
in the interval before, meets the demand for that interval.

Print the number of buses that start in each time slot (x) as a list of integers.
