# Lesson: redundant linking equality for products in z3_python optimization

The product production[t] * layout[t][v] is written as a sum of "k * production[t]" terms
guarded by layout == k. Z3's LP relaxation does not know that the printed copies add up to
n_slots * sheets. Stating that equality explicitly (sum of printed[v] == n_slots * total sheets)
took the 3 template instance from an execution timeout (attempt-001) to 74 s. A bit-vector
version with BV2Int objective (attempt-002) was slower, and timed out on both instances.
