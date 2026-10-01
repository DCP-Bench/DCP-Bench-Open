# Rehearsal problem: order the pieces of a concert for rehearsal so that the total time
# players spend present but not playing is as small as possible. A player arrives just
# before the first piece they play in and leaves just after the last.
import cpmpy as cp


def build(instance):
    num_pieces = instance["num_pieces"]
    num_players = instance["num_players"]
    duration = cp.cpm_array(instance["duration"])      # duration[q]: length of piece q
    plays = cp.cpm_array(instance["rehearsal"])        # plays[p][q] = 1 if player p plays in piece q

    # rehearsal_order[i] is the piece rehearsed in the i-th slot.
    rehearsal_order = cp.intvar(0, num_pieces - 1, shape=num_pieces, name="rehearsal_order")
    # arrival[p] is the first slot at which player p is present; departure[p] the last.
    arrival = cp.intvar(0, num_pieces - 1, shape=num_players, name="arrival")
    departure = cp.intvar(0, num_pieces - 1, shape=num_players, name="departure")

    model = cp.Model()

    # Every piece is rehearsed exactly once, so the order is a permutation of the pieces.
    model += cp.AllDifferent(rehearsal_order)

    # A player is present in every slot whose piece they play in: the slot lies between
    # their arrival and their departure.
    for p in range(num_players):
        for i in range(num_pieces):
            plays_in_slot = plays[p, rehearsal_order[i]] == 1
            model += plays_in_slot.implies((arrival[p] <= i) & (i <= departure[p]))

    # Waiting time: in every slot where a player is present but not playing, they wait for
    # the whole duration of the piece rehearsed in that slot.
    waiting_times = []
    for p in range(num_players):
        for i in range(num_pieces):
            present = (arrival[p] <= i) & (i <= departure[p])
            not_playing = plays[p, rehearsal_order[i]] == 0
            waiting_times.append(duration[rehearsal_order[i]] * (present & not_playing))

    # Minimise the total waiting time of all players.
    model.minimize(cp.sum(waiting_times))

    return model, {"rehearsal_order": rehearsal_order}
