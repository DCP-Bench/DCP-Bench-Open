# Rehearsal: order the pieces so that the total time players spend present but not playing is minimal.
from pycsp3 import *

num_pieces = data.num_pieces
num_players = data.num_players
duration = data.duration
rehearsal = data.rehearsal
max_duration = max(duration)

# rehearsal_order[i] is the piece rehearsed in slot i
rehearsal_order = VarArray(size=num_pieces, dom=range(num_pieces))
# slot_duration[i] is the duration of the piece in slot i
slot_duration = VarArray(size=num_pieces, dom=sorted(set(duration)))
# plays[p][i] = 1 if player p is involved in the piece of slot i
plays = VarArray(size=[num_players, num_pieces], dom={0, 1})
# before[p][i] = 1 if player p has a piece at slot i or earlier
before = VarArray(size=[num_players, num_pieces], dom={0, 1})
# after[p][i] = 1 if player p has a piece at slot i or later
after = VarArray(size=[num_players, num_pieces], dom={0, 1})
# waiting[p][i] = 1 if player p is present at slot i but not playing
waiting = VarArray(size=[num_players, num_pieces], dom={0, 1})
# wait_time[p][i] = time player p waits during slot i
wait_time = VarArray(size=[num_players, num_pieces], dom=range(max_duration + 1))

satisfy(
    # every piece is rehearsed in exactly one slot
    AllDifferent(rehearsal_order),
    # the duration of the piece in each slot comes from the piece's duration
    [Table(scope=[rehearsal_order[i], slot_duration[i]], supports=[(k, duration[k]) for k in range(num_pieces)]) for i in range(num_pieces)],
    # whether a player is involved in the piece of each slot comes from the rehearsal table
    [Table(scope=[rehearsal_order[i], plays[p][i]], supports=[(k, rehearsal[p][k]) for k in range(num_pieces)]) for p in range(num_players) for i in range(num_pieces)],
)

for p in range(num_players):
    satisfy(
        # a player is present from the first piece the player is in
        before[p][0] == plays[p][0],
        [before[p][i] >= before[p][i - 1] for i in range(1, num_pieces)],
        [before[p][i] >= plays[p][i] for i in range(num_pieces)],
        [before[p][i] <= before[p][i - 1] + plays[p][i] for i in range(1, num_pieces)],
        # a player is present until the last piece the player is in
        after[p][num_pieces - 1] == plays[p][num_pieces - 1],
        [after[p][i] >= after[p][i + 1] for i in range(num_pieces - 1)],
        [after[p][i] >= plays[p][i] for i in range(num_pieces)],
        [after[p][i] <= after[p][i + 1] + plays[p][i] for i in range(num_pieces - 1)],
        # a player waits in a slot when present there but not playing
        [waiting[p][i] <= before[p][i] for i in range(num_pieces)],
        [waiting[p][i] <= after[p][i] for i in range(num_pieces)],
        [waiting[p][i] <= 1 - plays[p][i] for i in range(num_pieces)],
        [waiting[p][i] >= before[p][i] + after[p][i] - 1 - plays[p][i] for i in range(num_pieces)],
        # the waiting time of a slot is the duration of its piece
        [If(waiting[p][i] == 1, Then=wait_time[p][i] == slot_duration[i], Else=wait_time[p][i] == 0) for i in range(num_pieces)],
    )

# minimise the total time players are waiting to play
minimize(Sum(wait_time))
