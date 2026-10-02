# Crew: assign flight attendants to flights so that every flight has the required
# number of crew with the required skills, and nobody works two flights in a row
# or has fewer than two flights off after one they worked.
import z3


def build(instance):
    attributes = instance["attributes"]        # attributes[p] = [steward, hostess, french, spanish, german]
    required_crew = instance["required_crew"]  # required_crew[f] = [staff, stewards, hostesses, french, spanish, german]
    num_persons = len(attributes)
    num_flights = len(required_crew)

    # crew[f][p] is true if person p is assigned to flight f.
    crew = [[z3.Bool(f"crew_{f}_{p}") for p in range(num_persons)] for f in range(num_flights)]
    # num_working is the number of persons working at least one flight.
    num_working = z3.Int("num_working")

    solver = z3.Solver()

    # The reference bounds the number of working persons between 1 and num_persons.
    solver.add(num_working >= 1, num_working <= num_persons)
    solver.add(num_working == z3.Sum([z3.If(z3.Or([crew[f][p] for f in range(num_flights)]), 1, 0)
                                      for p in range(num_persons)]))

    for f in range(num_flights):
        # Each flight has exactly the required number of cabin crew.
        solver.add(z3.PbEq([(crew[f][p], 1) for p in range(num_persons)], required_crew[f][0]))

        # The crew of the flight includes at least the required number of stewards,
        # hostesses, and French, Spanish and German speakers.
        for j in range(5):
            skilled = [(crew[f][p], attributes[p][j]) for p in range(num_persons)
                       if attributes[p][j] > 0]
            solver.add(z3.PbGe(skilled, required_crew[f][j + 1]))

    # After a flight a crew member rests for two flights: nobody works more than one
    # of any three consecutive flights.
    for f in range(num_flights - 2):
        for p in range(num_persons):
            solver.add(z3.AtMost(crew[f][p], crew[f + 1][p], crew[f + 2][p], 1))

    return solver, {"crew": crew}
