# session5_grocery plan (attempt 2)

Attempt 1 was accepted on 4 of 5 instances; the 711-cent, 4-item instance timed out (execution_timeout) with dom/wdeg search.
- "buys a number of items" -> num_items prices p_i >= 1 cent
- "The cashier charges a total price" -> sum of p_i = total_price
- "multiplied the items ... with adding them the price still comes to the same total" -> product of p_i = total_price * 100^(num_items - 1)
- "What were the prices of the items? Print the prices in cents" -> out.put("prices", p)
- search change: branch first on the first n-1 prices in input order (smallest first), then on the last price; no restarts. dom/wdeg on the same model timed out on the 711 instance.
- objective: none (satisfaction)
