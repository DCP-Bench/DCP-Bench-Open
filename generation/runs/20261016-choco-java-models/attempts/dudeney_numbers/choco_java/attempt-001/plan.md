Problem: a Dudeney number is a positive integer that is a perfect cube whose digit sum equals the cube root. Find one larger than 1. Input n = maximum number of digits.

- "positive integer with at most n digits" -> digits d_0..d_{n-1} in 0..9, number = sum d_i * 10^i -> m.scalar(digits, weights, "=", number)
- "digit sum equals the cube root" -> root s = sum d_i, s in 1..9n -> m.sum(digits, "=", root)
- "perfect cube" -> number = root^3 -> m.pow(root, 3, number)
- "larger than 1" -> number > 1 -> m.arithm(number, ">", 1)
- satisfaction, default search
