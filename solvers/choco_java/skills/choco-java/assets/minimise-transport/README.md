# Shipping plan (minimise)

**Problem:** ship from 2 warehouses (supply 20 and 30) to 3 shops (demand 10, 25 and 15) at minimum total cost. The cost table is in `Transport.java`.
**Shows:** a grid of integer flows, `sum` for supply and demand limits, `scalar` for the total cost, `setObjective(MINIMIZE, ...)`, and the proof check through `TERMINATED`.
**Run:** `java Transport.java`
**Expected:** `Minimum cost: 240`
**Expected:** `warehouse 0: 10 0 10`
