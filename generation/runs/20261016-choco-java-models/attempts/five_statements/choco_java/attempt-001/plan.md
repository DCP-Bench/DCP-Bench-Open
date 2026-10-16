Problem: five statements; each says "Exactly k of these statements are false" for k = 1..5. Output whether each is true (0/1, same order).
- Statement i (i = 1..5) is true iff exactly i statements are false -> exactly 5 - i statements are true.
- Output statements[i] as 0/1 for i = 1..5.
- Link each statement's truth value to the count of true statements (reified equality), using a sum over the Booleans.
Objective: none (satisfaction).
