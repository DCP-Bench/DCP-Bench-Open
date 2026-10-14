Output domains in the description are 1-based (columns 1..n): declare the IntVarArray with 1..n directly so the output needs no shift.
The diagonal rules are `distinct` with offset arrays (i and -i) at IPL_DOM; no decomposition was needed.
Quick check and full evaluation both passed on the first attempt; the per-instance solve times were about 1 ms.
