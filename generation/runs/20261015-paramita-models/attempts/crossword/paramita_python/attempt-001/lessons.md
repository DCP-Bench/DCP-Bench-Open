Slot-to-word grids are cheap: one-hot per (slot, word) with a length filter; crossings are pairwise clauses ~(w[a][u] & w[b][v]) for mismatched letters.
The problem's data is fixed by the statement with no instance fields, so grid and words are constants in the model, with a comment saying so.
