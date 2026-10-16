The farmer, wolf, goat and cabbage start on the starting shore (0) and must all reach the destination shore (1) -> wolf_pos[0]=goat_pos[0]=cabbage_pos[0]=boat_pos[0]=0 and wolf_pos[S-1]=goat_pos[S-1]=cabbage_pos[S-1]=boat_pos[S-1]=1
The boat can carry only the farmer and a single item -> per stage step: wolf, goat, cabbage changes sum to at most 1 (sum <= 1 over the change Booleans)
The boat alternates between the shores on each crossing -> boat_pos[t] != boat_pos[t+1] (arithm !=)
An item can only move with the farmer -> if an item changes shore between t and t+1, it is on the boat's shore at t (ifThen)
If left unattended together, the wolf would eat the goat -> at each stage: wolf == goat implies the boat is with them (goat == boat)
or the goat would eat the cabbage -> at each stage: goat == cabbage implies the boat is with them (goat == boat)
Print whether the wolf, goat, cabbage, and boat are on the destination shore -1- or the starting shore -0- at each stage -> outputs wolf_pos, goat_pos, cabbage_pos, boat_pos as BoolVar arrays of length stage (S)
Objective: satisfaction (no objective)
