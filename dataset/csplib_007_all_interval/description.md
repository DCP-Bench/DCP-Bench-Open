Given the twelve standard pitch-classes (c, c#, d, …), represented by numbers \(0, 1, \ldots, 11\), find a series
in which each pitch-class occurs exactly once and in which the musical intervals between neighbouring notes cover
the full set of intervals from the minor second (1 semitone) to the major seventh (11 semitones). That is, for each
of the intervals, there is a pair of neighbouring pitch-classes in the series, between which this interval appears.

The problem of finding such a series can be easily formulated as an instance of a more general arithmetic problem
on \(\mathbb{Z}_n\), the set of integer residues modulo \(n\). Given \(n \in \mathbb{N}\), find a vector
\(s = (s_1, \ldots, s_n)\), such that

- \(s\) is a permutation of \(\mathbb{Z}_n = \{0, 1, \ldots, n-1\}\); and
- the interval vector \(v = (|s_2 - s_1|, |s_3 - s_2|, \ldots, |s_n - s_{n-1}|)\) is a permutation of
  \(\mathbb{Z}_n \setminus \{0\} = \{1, 2, \ldots, n-1\}\).

A vector \(v\) satisfying these conditions is called an all-interval series of size \(n\); the problem of finding
such a series is the all-interval series problem of size \(n\).

Print the sequence of pitch-classes (x) as a list of n integers -between 0 and n-1- and the corresponding intervals (diffs)
as a list of n-1 integers.
