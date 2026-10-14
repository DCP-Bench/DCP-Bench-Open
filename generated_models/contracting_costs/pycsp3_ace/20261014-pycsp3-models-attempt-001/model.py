from pycsp3 import *

# Six men (paper hanger, painter, plumber, electrician, carpenter, mason) each charge a price in dollars.
paper_hanger = Var(dom=range(0, 10001))
painter = Var(dom=range(0, 10001))
plumber = Var(dom=range(0, 10001))
electrician = Var(dom=range(0, 10001))
carpenter = Var(dom=range(0, 10001))
mason = Var(dom=range(0, 10001))

satisfy(
    # $1,100 is paid to the paper hanger and the painter
    paper_hanger + painter == 1100,
    # $1,700 is paid to the painter and plumber
    painter + plumber == 1700,
    # $1,100 is paid to the plumber and electrician
    plumber + electrician == 1100,
    # $3,300 is paid to the electrician and carpenter
    electrician + carpenter == 3300,
    # $5,300 is paid to the carpenter and mason
    carpenter + mason == 5300,
    # $3,200 is paid to the mason and painter
    mason + painter == 3200,
)
