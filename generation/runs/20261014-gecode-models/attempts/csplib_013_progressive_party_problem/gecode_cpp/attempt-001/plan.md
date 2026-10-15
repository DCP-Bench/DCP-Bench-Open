# Plan: progressive party problem (attempt 1)

Variables: host[b] Bool (is_host); vis[p*n+b] Int in 0..n-1 (boat b visits boat v in period p); total = sum(host).

- "a host boat remains on board to act as host" -> host[b] >> vis[p,b] == b, per period -> reified rel (MiniModel)
- "the crew of a guest boat together visits several hosts": a guest visits a host boat in every period, the visited boat must be a host -> element(BoolVarArgs host, vis[p,b], 1) (element over host bools)
- a guest boat does not visit itself -> !host[b] >> vis[p,b] != b -> reified rel
- "a guest boat cannot revisit a host": the guest's visited boats are pairwise distinct over the periods -> distinct(BoolVarArgs guest-flags, IntVarArgs vis over periods) (selected distinct; hosts are not selected)
- "every boat can only hold a limited number of people at a time (capacity)": for each period p and host h, sum of crew[g] over g with vis[p,g] == h <= cap[h] -> linear(IntArgs crew, BoolVarArgs eq-flags, IRT_LQ, cap[h]). Non-hosts receive no visits, so this bounds them trivially.
- "crew sizes differ" -> weights are crew_size
- "guest crews cannot meet more than once": for each pair of boats a<b, the number of periods with vis[p,a] == vis[p,b] is at most 1 -> linear(BoolVarArgs eq-flags, IRT_LQ, 1). Pairs with a host cannot exceed 1 already (no revisit), so the uniform form is safe.
- Branching: host bools first, value 0 first (BOOL_VAL_MIN) because the objective is to minimise hosts; then vis with INT_VAR_SIZE_MIN, INT_VAL_MIN.
- Objective: minimise the number of hosts, nhosts = sum(host), minimize(nhosts).
- Symmetry breaking is not included (commented out in the reference, so not part of the contract).
