from pycsp3 import *

# four people hold eight jobs; each job is given the index (0 to 3) of the person who holds it
chef = Var(dom=range(4))
guard = Var(dom=range(4))
nurse = Var(dom=range(4))
clerk = Var(dom=range(4))
police_officer = Var(dom=range(4))
teacher = Var(dom=range(4))
actor = Var(dom=range(4))
boxer = Var(dom=range(4))
jobs = [chef, guard, nurse, clerk, police_officer, teacher, actor, boxer]
satisfy(
    # each person holds exactly two jobs
    [Count(jobs, value=p) == 2 for p in range(4)],
    # the nurse is not a teacher, police officer, or clerk
    nurse != teacher,
    nurse != police_officer,
    nurse != clerk,
    # the clerk is not the chef
    clerk != chef,
    # person 0 is not the boxer
    boxer != 0,
    # person 3 is not the teacher, police officer, or nurse
    teacher != 3,
    police_officer != 3,
    nurse != 3,
    # person 0, the chef, and the police officer went golfing together: three different people
    chef != 0,
    police_officer != 0,
    chef != police_officer,
)
