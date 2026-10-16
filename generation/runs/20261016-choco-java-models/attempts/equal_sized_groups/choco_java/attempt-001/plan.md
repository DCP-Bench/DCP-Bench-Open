# equal_sized_groups: plan (Choco 6.0.1)

I have a sorted list of N elements, and I want to divide them into K groups, by choosing K-1 split points
  -> cut[i] in IntVar[K-1], domain = valid split positions 1..N-1 (from the instance array a)
There may be elements with the same value, and it is necessary to have items with same value in the same group.
  -> cut domain restricted to c with a[c-1] != a[c] (data-derived domain, no extra constraint)
Find K groups ... (groups must be in order, none empty)
  -> m.increasing(cut, 1) (strict)
Group size of group j = prefix[j+1] - prefix[j], prefix[0] = 0, prefix[K] = N
  -> IntVar expressions prefix[j+1].sub(prefix[j]).intVar()
as close in size to round(N/K) as possible (error = abs(size - round(N/K)))
  -> m.absolute(error[j], size - ideal)
total error minimized (objective)
  -> m.sum(error) with Model.MINIMIZE
Output x: break points = cut[i] (1-based index of last element of group i)
  -> out.put("x", cut)
Search: branch on cut in input order, smallest first.
