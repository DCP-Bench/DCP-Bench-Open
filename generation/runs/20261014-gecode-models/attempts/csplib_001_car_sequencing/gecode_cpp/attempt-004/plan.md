A number of cars are to be produced, of different types -> one slot variable per car, value = internal type; count(*this, slot, cards, vals, IPL_DOM) with cards fixed to the demand of each type (gcc)
different options are available as variants -> per slot one 0/1 variable per option, tied to the type by TupleSet (type, o1..ok) -> extensional(*this, row, table) (joint domain consistency, stronger than one element per option)
stations handle at most a certain share of the cars; cars requiring an option must not be bunched -> per option sequence(*this, need[o], IntSet(1,1), per_slots[o], 0, at_most[o], IPL_DOM)
implied: first t slots hold at most a*(t/q)+min(a,t%q) cars needing the option, and at least total minus that bound for the rest -> linear(*this, prefix, IRT_LQ / IRT_GQ, bound) (skill Search section)
print the sequence of car types, 0-based -> element(*this, IntArgs(order), slot[i], type[i]); output type
branching -> slots in order (INT_VAR_NONE), INT_VAL_MIN; types renumbered by option utilisation (most used option first), lexicographic over options
objective -> none (satisfaction)
