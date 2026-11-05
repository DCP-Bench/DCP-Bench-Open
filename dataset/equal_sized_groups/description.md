I have a sorted list of N elements, and I want to divide
them into K groups, by choosing K-1 split points between them. There may be
elements with the same value, and it is necessary to have items with same value in
the same group. Find K groups as close in size to round(N/K) as possible.

For example, divide these 32 elements into 4 groups, as close to 8 elements in each group as possible (32/4=8):

```text
1 1 1 1 2 2 3 3 3 3 3 3 3 3 4 4 4 4 5 5 5 5 5 6 6 6 6 7 8 9 10 10
```

One solution would be these 3 break points:

```text
1 1 1 1 2 2 | 3 3 3 3 3 3 3 3 | 4 4 4 4 5 5 5 5 5 | 6 6 6 6 7 8 9 10 10
[            6                 14                 23                    ]
[6 elements     8 elements          9 elements         9 elements       ]
```

```text
1 1 1 1 2 2         = 6 elements,  error = abs(8-6)=2
3 3 3 3 3 3 3 3     = 8 elements,  error = abs(8-8)=0
4 4 4 4 5 5 5 5 5     = 9 elements,  error = abs(8-9)=1
6 6 6 6 7 8 9 10 10 = 9 elements,  error = abs(8-9)=1

total error = 4 (2+0+1+1)
break points = [6, 14, 23]
```

Each group holds at least one element. Print, for the given list `a` and number of groups `k`, the `k`-1 break points (x),
where a break point is the number of elements before it, such that the total error is minimized.
