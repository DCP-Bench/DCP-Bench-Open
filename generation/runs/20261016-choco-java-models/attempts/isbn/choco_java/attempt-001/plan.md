Problem: isbn. Given 13 digits where -1 is unknown, fill the unknown digits so the number is a valid ISBN-13 that starts with 978 or 979.

- 13 digits 0..9, each given digit is kept -> isbn[i] = given digit (eq(v).post()) where given != -1
- must start with 978 or 979 -> isbn[0] = 9, isbn[1] = 7, isbn[2] in {8, 9} (arithm >= 8)
- multiply digits alternately by 1 and 3 (starting with 1), sum the products -> m.scalar(isbn, weights, "=", total), weights 1,3,1,3,...,1
- check digit is (10 - sum % 10) % 10, so the weighted total is divisible by 10 -> total mod 10 = 0
- objective: none, satisfaction; output isbn -> out.put("isbn", isbn)
