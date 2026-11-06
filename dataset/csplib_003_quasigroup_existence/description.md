An order m quasigroup is a Latin square of size m. That is, a $m \times m$ multiplication table in which each element
occurs once in every row and column. For example,

```
1    2   3   4
4    1   2   3
3    4   1   2
2    3   4   1
```

is an order 4 quasigroup. A quasigroup can be specified by a set and a binary multiplication operator, \* defined over
this set. Quasigroup existence problems determine the existence or non-existence of quasigroups of a given size with
additional properties. Certain existence problems are of sufficient interest that a naming scheme has been invented
for them. We define two new relations, \*321 and \*312 by $a \*321 b = c$ iff $c\*b=a$ and
$a \*312 b = c$ iff $b\*c=a$.

QG3.m problems are order m quasigroups for which $(a\*b)\*(b\*a) = a$.
We only consider the QG3.m problem for this task.

Print the quasigroup (quasigroup) as a list of lists of integers from 0 to m-1.
