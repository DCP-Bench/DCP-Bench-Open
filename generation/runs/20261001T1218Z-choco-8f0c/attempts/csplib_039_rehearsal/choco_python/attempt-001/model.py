# Rehearsal problem: put the pieces of a concert in a rehearsal order so that the
# total time that players are present but not playing is as small as possible.
# A player arrives just before the first piece they play in and leaves just after
# the last one.
from pychoco.model import Model


def build(instance):
    num_pieces = instance["num_pieces"]
    num_players = instance["num_players"]
    duration = instance["duration"]  # duration[j] = length of piece j
    rehearsal = instance["rehearsal"]  # rehearsal[p][j] = 1 if player p plays in piece j

    model = Model()

    # rehearsal_order[i] = the piece rehearsed in the i-th slot
    rehearsal_order = [model.intvar(0, num_pieces - 1, name=f"rehearsal_order_{i}") for i in range(num_pieces)]
    # arrival[p] = first slot in which player p is present, departure[p] = last slot
    arrival = [model.intvar(0, num_pieces - 1, name=f"arrival_{p}") for p in range(num_players)]
    departure = [model.intvar(0, num_pieces - 1, name=f"departure_{p}") for p in range(num_players)]

    # each piece is rehearsed exactly once, so the order is a permutation
    model.all_different(rehearsal_order).post()

    # slot_duration[i] = length of the piece rehearsed in slot i
    slot_duration = [model.intvar(min(duration), max(duration), name=f"slot_duration_{i}")
                     for i in range(num_pieces)]
    for i in range(num_pieces):
        model.element(slot_duration[i], duration, rehearsal_order[i]).post()

    waiting_times = []
    for p in range(num_players):
        for i in range(num_pieces):
            # playing[p][i] = 1 if player p plays in the piece rehearsed in slot i
            playing = model.boolvar(name=f"playing_{p}_{i}")
            model.element(playing, rehearsal[p], rehearsal_order[i]).post()

            # present[p][i] = 1 if slot i lies between the arrival and departure of player p
            arrived = model.arithm(arrival[p], "<=", i).reify()
            not_yet_gone = model.arithm(departure[p], ">=", i).reify()
            present = model.sum([arrived, not_yet_gone], "=", 2).reify()

            # a player who plays in a slot must be present in it
            model.arithm(playing, "<=", present).post()

            # the player waits in slot i if present but not playing; as playing implies
            # present, that is present - playing
            waiting = model.intvar(0, 1, name=f"waiting_{p}_{i}")
            model.arithm(present, "-", playing, "=", waiting).post()

            # a waiting player waits for the whole duration of the piece in that slot
            waiting_time = model.intvar(0, max(duration), name=f"waiting_time_{p}_{i}")
            model.times(slot_duration[i], waiting, waiting_time).post()
            waiting_times.append(waiting_time)

    # total time that players are present but not playing
    total_waiting = model.intvar(0, num_players * sum(duration), name="total_waiting")
    model.sum(waiting_times, "=", total_waiting).post()

    # minimise the total waiting time
    return model, {"rehearsal_order": rehearsal_order}, ("minimize", total_waiting)
