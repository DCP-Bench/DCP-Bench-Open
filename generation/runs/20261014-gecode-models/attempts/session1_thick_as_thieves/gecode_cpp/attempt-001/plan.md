Problem: six suspects, each makes one statement; innocent tell the truth, guilty lie; the car holds two, so at most two are guilty. Who is guilty?
Variables: guilty[k] Boolean per suspect (artie, bill, crackitt, dodgy, edgy, fingers); n_guilty = sum(guilty).
- the getaway car was barely big enough to hold two -> n_guilty <= 2 -> rel(*this, n_guilty, IRT_LQ, 2)
- a robbery was committed, so someone did it -> n_guilty >= 1 -> rel(*this, n_guilty, IRT_GQ, 1)
- each suspect is guilty exactly when the statement is false (innocent truthful, guilty lying) -> guilty[k] == !statement[k], one reified equality per suspect, as in the rows below
- ARTIE: "It wasn't me." -> statement is not guilty[artie]; the rule gives guilty[artie] == !!guilty[artie], always true, no post; comment only
- BILL: "Crackitt was in it up to his neck." -> statement is guilty[crackitt] -> rel(*this, guilty[bill] == !guilty[crackitt])
- CRACKITT: "No I wasn't." -> statement is not guilty[crackitt]; always consistent, no post; comment only
- DODGY: "If Crackitt did it, Bill did it with him." -> statement is guilty[crackitt] >> guilty[bill]; its negation is crackitt and not bill -> rel(*this, guilty[dodgy] == (guilty[crackitt] && !guilty[bill])) (Boolean connectives in MiniModel)
- EDGY: "Nobody did it alone." -> statement is n_guilty != 1; negation n_guilty == 1 -> rel(*this, guilty[edgy] == (n_guilty == 1))
- FINGERS: "Artie and Dodgy together." -> statement is the guilty set equals {artie, dodgy}: guilty[artie] && guilty[dodgy] && n_guilty == 2; rel(*this, guilty[fingers] == !(guilty[artie] && guilty[dodgy] && n_guilty == 2))
- branching: BOOL_VAR_NONE over guilty (six Booleans, all decision variables), BOOL_VAL_MIN; no objective (satisfaction).
- instance: no fields; constructor ignores the argument except (void)instance.
