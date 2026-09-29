# Rehearsal problem: order the pieces of a concert for rehearsal so that the
# total time players spend present but not playing is minimal. A player arrives
# just before the first piece they play in and leaves after the last one.
from ortools.sat.python import cp_model


def build(instance):
    n_pieces = instance["num_pieces"]
    n_players = instance["num_players"]
    duration = instance["duration"]  # rehearsal time of each piece
    rehearsal = instance["rehearsal"]  # rehearsal[p][j] = 1 if player p plays in piece j

    model = cp_model.CpModel()

    # rehearsal_order[i] = the piece rehearsed in slot i; each piece is rehearsed exactly once
    rehearsal_order = [model.new_int_var(0, n_pieces - 1, f"order_{i}") for i in range(n_pieces)]
    model.add_all_different(rehearsal_order)

    # the length of the piece in each slot, and whether each player plays in it;
    # both are looked up in the data by the (variable) piece number
    slot_duration = []
    plays = [[None] * n_pieces for _ in range(n_players)]
    for i in range(n_pieces):
        d = model.new_int_var(min(duration), max(duration), f"slot_duration_{i}")
        model.add_element(rehearsal_order[i], duration, d)
        slot_duration.append(d)
        for p in range(n_players):
            flag = model.new_bool_var(f"plays_{p}_{i}")
            model.add_element(rehearsal_order[i], rehearsal[p], flag)
            plays[p][i] = flag

    # arrival[p] / departure[p] = first / last slot in which player p is present
    arrival = [model.new_int_var(0, n_pieces - 1, f"arrival_{p}") for p in range(n_players)]
    departure = [model.new_int_var(0, n_pieces - 1, f"departure_{p}") for p in range(n_players)]

    waiting = []
    for p in range(n_players):
        for i in range(n_pieces):
            # a player who plays in slot i must be present in it
            model.add(arrival[p] <= i).only_enforce_if(plays[p][i])
            model.add(departure[p] >= i).only_enforce_if(plays[p][i])

            # present = between arrival and departure
            after_arrival = model.new_bool_var(f"after_arrival_{p}_{i}")
            model.add(arrival[p] <= i).only_enforce_if(after_arrival)
            model.add(arrival[p] > i).only_enforce_if(after_arrival.negated())
            before_departure = model.new_bool_var(f"before_departure_{p}_{i}")
            model.add(departure[p] >= i).only_enforce_if(before_departure)
            model.add(departure[p] < i).only_enforce_if(before_departure.negated())

            # waiting = present but not playing; it costs the length of the piece in that slot
            wait = model.new_bool_var(f"wait_{p}_{i}")
            model.add_bool_and([after_arrival, before_departure, plays[p][i].negated()]).only_enforce_if(wait)
            model.add_bool_or([after_arrival.negated(), before_departure.negated(), plays[p][i]]).only_enforce_if(
                wait.negated()
            )
            cost = model.new_int_var(0, max(duration), f"wait_time_{p}_{i}")
            model.add_multiplication_equality(cost, [slot_duration[i], wait])
            waiting.append(cost)

    # minimise the total time players spend waiting
    model.minimize(sum(waiting))

    return model, {"rehearsal_order": rehearsal_order}
