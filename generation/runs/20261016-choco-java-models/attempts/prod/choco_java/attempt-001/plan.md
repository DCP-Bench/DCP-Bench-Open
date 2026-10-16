Problem: prod. Choose production quantities X[j] for each product j, 0 <= X[j] <= u[j], so that the sum of X[j] / a[j] stays within b, and maximise the total profit sum of c[j] * X[j].

- production of product j between 0 and u[j] -> X[j] IntVar in 0..u[j]
- sum of (1/a[j]) * X[j] <= b -> multiply by L = lcm(a) to keep integers: m.scalar(X, L/a[j], "<=", b*L)
- total profit = sum of c[j] * X[j] -> m.scalar(X, c, "=", total_profit)
- objective: maximise total profit -> m.setObjective(Model.MAXIMIZE, total_profit)
- output x -> out.put("x", X); total_profit -> out.put("total_profit", total_profit)
