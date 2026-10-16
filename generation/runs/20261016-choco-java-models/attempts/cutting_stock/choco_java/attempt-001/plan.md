Cutting stock: raw rolls of width RollWidth cut into pieces of the given widths, each cutting pattern is a list of piece counts per width
"a set of widths to be cut, each width has a number of orders" -> per width w: sum over patterns of (pattern count of w) * used_p >= orders_w
"how many times each pattern is used" -> used_p integer in 0..max order (decision variables)
"minimise the total number of raw rolls cut" -> total = sum of used_p, minimise total
Note: "meets the total Orders" read as at least the order (>=)
objective -> minimise total rolls
