# Lessons from attempts 001-004

- 001: objective as one soft clause per shipped unit (weight = unit cost), total_cost
  tied by an adder equality over its 10000 order thresholds. Only json:3 (2 regions)
  accepted, in 150 s; the rest timed out.
- 002: one-direction tie (cost <= total) over the shipment thresholds, objective on
  grouped total thresholds. json:3 in 3.5 s; the 3+ region instances timed out.
- 003: shipments to each region ranked by unit cost; cost rewritten as cheapest cost
  * demand plus cost steps * units from dearer ranks, the rank levels order-encoded and
  linked by three-literal clauses; total tied exactly via its binary digits (adder);
  objective on the cost-step terms. 4/5 accepted (example 41 s); json:4 hit the
  2048 MB memory limit.
- 004: as 003 but objective on grouped total thresholds. 4/5 accepted, all under 4 s;
  json:4 (5 regions) still times out (execution_timeout, 178 s).

The remaining weak link is the adder that ties the cost terms to total_cost; a BDD
over the ~840 terms plus the total would be millions of nodes.
