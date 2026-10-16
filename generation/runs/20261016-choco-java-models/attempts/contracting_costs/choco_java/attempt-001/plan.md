# contracting_costs plan (attempt-001)

Variables: the charge of each man, in dollars: paper_hanger, painter, plumber, electrician, carpenter, mason (0..10000, bounds-only).
- "$1,100 to the paper hanger and the painter" -> paper_hanger + painter = 1100 -> m.sum
- "$1,700 to the painter and plumber" -> painter + plumber = 1700
- "$1,100 to the plumber and electrician" -> plumber + electrician = 1100
- "$3,300 to the electrician and carpenter" -> electrician + carpenter = 3300
- "$5,300 to the carpenter and mason" -> carpenter + mason = 5300
- "$3,200 to the mason and painter" -> mason + painter = 3200
- Objective: none (satisfaction).
