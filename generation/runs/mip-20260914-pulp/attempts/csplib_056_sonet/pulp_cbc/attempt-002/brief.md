# csplib_056_sonet
Instance: `r`, `n`, `demand`, `capacity_nodes`. Output: `ring_config`, an
r x n 0/1 matrix. Minimize the number of node-to-ring assignments so that every
demanding pair shares a ring and no ring exceeds its node capacity.
The shared-ring test is a conjunction of two binaries, which MIP cannot state
directly; it is linearised with one indicator per ring.
