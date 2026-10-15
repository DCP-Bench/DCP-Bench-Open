Given a collection of integers, find a number of elements that sum to zero. -> Bool b_i per element (indices), 
Print whether each element is selected (indices) as a list of booleans. -> outputs indices = list of the b_i
Select m elements (m is the instance field) -> sum(b_i) == m (PB, unit weights)
The selected elements sum to zero -> sum(nums[i] * b_i) == 0 (PB with signed integer weights)
Objective: none (satisfaction)
