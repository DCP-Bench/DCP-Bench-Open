# Plan: csplib_039_rehearsal

- "devise an order in which the pieces can be rehearsed" -> pos[j][s] one-hot Bool (piece j in slot s); output rehearsal_order[s] = sum_j j*pos[j][s]
- "each piece is rehearsed once" -> per piece j: sum_s pos[j][s] == 1
- "each slot is one piece" -> per slot s: sum_j pos[j][s] == 1
- "each involving a different combination of the members" -> plays[p][s] <-> OR_{j: rehearsal[p][j]=1} pos[j][s] (Iff)
- "players arrive immediately before the first piece in which they are involved" -> started[p][s] <-> started[p][s-1] | plays[p][s] (unary-style prefix Or)
- "and depart immediately after the last piece" -> finished[p][s] <-> finished[p][s+1] | plays[p][s] (suffix Or)
- "total time when players are present but not currently playing" -> waiting[p][s] <-> started & finished & ~plays
- "time" = duration of the piece in the slot -> aux a[p][s][j] <-> waiting[p][s] & pos[j][s], weight duration[j]
- objective "minimize the total time players are waiting" -> minimise sum a[p][s][j]*duration[j] (the total_waiting expression)
