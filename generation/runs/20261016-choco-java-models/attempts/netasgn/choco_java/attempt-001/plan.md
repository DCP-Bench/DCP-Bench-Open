# netasgn plan

- "Given a set of people People and a set of projects Projects" -> index ranges from inst supply (people) and demand (projects); no constraint
- "Each person i has a certain number of available hours Supply_{i}" and "the total number of hours assigned from each person i equals its supply" -> m.sum(assign[i], "=", supply[i]).post()
- "each project j requires a certain number of hours Demand_{j}" and "the total number of hours assigned to each project j equals its demand" -> m.sum(column j, "=", demand[j]).post()
- "Each person i can contribute to project j up to a maximum limit Limit_{i, j}" -> domain of assign[i][j] is 0..limit[i][j]
- "The cost per hour of work for person i on project j is Cost_{i, j}" and "minimize the total cost of assigning people to projects" -> total_cost = m.scalar(all assign, cost flattened, total_cost); setObjective MINIMIZE
- "Print the hours assigned from each person to each project (assign)" -> out.put("assign", assign)
- "and the total cost (total_cost)" -> out.put("total_cost", total)
