Sizing an index type and a value type from one scalar works: type Idx := {1..${n}} and type Val := {0..${n}}, with the bound n-1 as a constraint on n().
Counting with #{ j in Idx: x(j) = i - 1 } = x(i) over a 1-based index gave the 0-based sequence and was accepted on all 9 instances.
