Problem: nine distinct non-zero digits A..I with A/BC + D/EF + G/HI = 1, BC/EF/HI two-digit numbers.

- "nine distinct non-zero digits" -> domains 1..9, `distinct(*this, digits, IPL_DOM)` (the nine digits are a permutation of 1..9)
- "BC, EF, HI are two-digit numbers formed by B and C, E and F, H and I" -> `expr(*this, 10*B + C)` etc. (linear views, bounds from the digits)
- "A/BC + D/EF + G/HI = 1" without division -> multiply by BC*EF*HI: A*EF*HI + D*BC*HI + G*BC*EF == BC*EF*HI, with the products as `expr(*this, x*y)` (default propagation; domains are small, at most 99*99*99)
- branching -> `branch(*this, digits, INT_VAR_SIZE_MIN(), INT_VAL_MIN())` over A..I; the two-digit numbers and products are fixed by propagation once their digits are set
- objective -> none (satisfaction); the driver enumerates solutions up to the limit
