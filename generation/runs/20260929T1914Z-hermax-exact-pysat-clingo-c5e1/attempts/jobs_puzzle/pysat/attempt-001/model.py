# Jobs puzzle: four people hold eight different jobs, two each, subject to
# clues about who is not what.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n_people = 4

    pool = IDPool()
    # job[name] = the person, 0-3, who holds that job
    job = {name: Integer(name, 0, n_people - 1, vpool=pool) for name in JOBS}
    engine = IntegerEngine(vars=list(job.values()), vpool=pool)
    cnf = engine.clausify()

    # every person holds exactly two jobs
    for person in range(n_people):
        cnf.extend(CardEnc.equals(lits=[job[name].equals(person) for name in JOBS], bound=2,
                                  vpool=pool, encoding=EncType.seqcounter).clauses)

    def apart(first, second):
        # the two jobs are held by different people
        for person in range(n_people):
            cnf.append([-job[first].equals(person), -job[second].equals(person)])

    def not_held_by(name, person):
        cnf.append([-job[name].equals(person)])

    # 1. the nurse is not the teacher, the police officer or the clerk
    apart("nurse", "teacher")
    apart("nurse", "police_officer")
    apart("nurse", "clerk")
    # 2. the clerk is not the chef
    apart("clerk", "chef")
    # 3. person 0 is not the boxer
    not_held_by("boxer", 0)
    # 4. person 3 is not the teacher, the police officer or the nurse
    not_held_by("teacher", 3)
    not_held_by("police_officer", 3)
    not_held_by("nurse", 3)
    # 5. person 0, the chef and the police officer went golfing together, so they
    # are three different people
    not_held_by("chef", 0)
    not_held_by("police_officer", 0)
    apart("chef", "police_officer")

    return cnf, job
