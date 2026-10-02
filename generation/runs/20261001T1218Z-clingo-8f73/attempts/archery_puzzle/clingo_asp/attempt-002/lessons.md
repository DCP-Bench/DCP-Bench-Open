# Lesson from the second attempt (rejected: invalid_solution)

The score was a derived atom (`score(S)`) that exists only when a running-total chain reaches
the end. A choice of hits whose total passes the bound has no `score`, hence no `deviation`
atom, hence cost 0 for `#minimize`: clingo reported it as optimal and the reference could not
extend it. When an objective is built from derived atoms, add `:- not score(_).` so the absence
of the atom is a conflict instead of a free zero-cost model. The clingo-asp skill's Optimization
section does not say this.
