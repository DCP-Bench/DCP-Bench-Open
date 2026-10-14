the printer makes a number of distinct templates (n_templates) -> one row of layout counts per template, fixed count from the instance
each template has n_slots positions -> linear(*this, row_t, IRT_EQ, n_slots) over the layout row
each variation v has copies on each template, layout[t][v] in 0..n_slots -> IntVarArray layout(*this, T*V, 0, n_slots)
each template t is printed production[t] times -> IntVarArray production(*this, T, 0, max(demand)); a sheet printed more than max(demand) times over-supplies every variation on it, so no optimum is lost
copies of v printed from t = production[t] * layout[t][v] -> printed[t][v] = rel(production[t] * layout[t][v]) (a product, no global fits)
the copies on template t are n_slots times its sheets (rows of the printed matrix) -> linear(printed row t) - n_slots*production[t] == 0 (implied by the full-template rule)
each variation v is printed at least demand[v] copies in total -> linear(printed column v, IRT_GQ, demand[v])
copies of v cannot exceed what the other variations leave -> linear(printed column v) - n_slots*sum(production) <= demand[v] - sum(demand) (implied; prunes the search: the 3-template instance is tight, 7 spare copies in total)
sheets are at least total demand over n_slots -> linear(sum(production), IRT_GQ, ceil(sum(demand)/n_slots)) (implied)
templates are interchangeable -> lex order on consecutive layout rows rel(row_t, IRT_LQ, row_t+1) (valid: permuting templates keeps every constraint and the objective)
minimise the total number of printed sheets -> total = expr(sum(production)), minimize(total)
branching -> production first (INT_VAR_SIZE_MIN, INT_VAL_SPLIT_MIN), then layout (INT_VAR_SIZE_MIN, INT_VAL_MAX)
