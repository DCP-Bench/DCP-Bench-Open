Connect matching colors with pipe to create a flow; pair all colors -> each colour's cells form one pipe between its two given endpoints
cover the entire board -> B[p] in 1..K for every cell p (domain of the colour variable)
given cells keep their colour (1 0 0 2 3 ...) -> rel(*this, B[p], IRT_EQ, v) for every nonzero entry
pipes do not cross or overlap -> one colour per cell (B is a single IntVar per cell), no two pipes share a cell
each pipe end has exactly one same-colour neighbour -> linear(*this, edge bools at p, IRT_EQ, 1) at endpoints (no map row; a degree count over a Boolean edge set, reified with expr(B[p] == B[q]))
each interior pipe cell has exactly two same-colour neighbours -> linear(*this, edge bools at p, IRT_EQ, 2)
no separate loop of a colour away from its ends -> steps d[p]: endpoints d = 0, others d >= 1, and each interior cell has a same-colour neighbour q with d[q] = d[p] - 1 (reified with expr, clause BOT_OR); a strictly decreasing chain rules out cycles (no map row; a path ordering decomposition, justified by the cycle-free requirement)
branching -> branch on B first (first fail, min value), then on d (min value) so every auxiliary is fixed
objective -> none (satisfaction)
