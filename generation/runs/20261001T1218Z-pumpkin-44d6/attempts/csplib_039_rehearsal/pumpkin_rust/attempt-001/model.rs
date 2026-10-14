// Rehearsal: order the pieces of a concert for rehearsal so that the total time
// players spend waiting is as small as possible. A player arrives just before
// the first piece they play in and leaves just after the last one, and waits
// during every piece in between that they do not play in.

type Tag = pumpkin_solver::core::proof::ConstraintTag;

// Post "at least one of these literals is true".
fn post_clause(solver: &mut Solver, lits: Vec<Lit>, tag: Tag) {
    solver.add_constraint(pumpkin_solver::clause(lits, tag)).post();
}

// Post "exactly one of these literals is true".
fn exactly_one(solver: &mut Solver, lits: Vec<Lit>, tag: Tag) {
    let n = lits.len();
    post_clause(solver, lits.clone(), tag);
    solver
        .add_constraint(pumpkin_solver::boolean_less_than_or_equals(vec![1; n], lits, 1, tag))
        .post();
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("num_pieces"); // number of pieces, and of rehearsal slots
    let num_players = inst.size("num_players");
    let duration = inst.ints("duration"); // duration[q]: length of piece q
    let rehearsal = inst.matrix("rehearsal"); // rehearsal[p][q] == 1 when player p plays in piece q

    // slot_has[i][q] is true when piece q is rehearsed in slot i. Every slot
    // holds exactly one piece and every piece is in exactly one slot, so the
    // rehearsal order is a permutation of the pieces (the reference's AllDifferent).
    let slot_has: Vec<Vec<Lit>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();
    let permutation = solver.new_constraint_tag();
    for i in 0..n {
        exactly_one(solver, slot_has[i].clone(), permutation);
    }
    for q in 0..n {
        exactly_one(solver, (0..n).map(|i| slot_has[i][q]).collect(), permutation);
    }

    // rehearsal_order[i] is the piece rehearsed in slot i, i.e. the q with
    // slot_has[i][q] true: rehearsal_order[i] = sum(q * slot_has[i][q]).
    let rehearsal_order: Vec<Var> = (0..n)
        .map(|_| solver.new_bounded_integer(0, n as i32 - 1))
        .collect();
    let channel = solver.new_constraint_tag();
    for i in 0..n {
        let mut terms: Vec<Term> = vec![rehearsal_order[i].scaled(1)];
        for q in 1..n {
            terms.push(slot_has[i][q].get_integer_variable().scaled(-(q as i32)));
        }
        solver
            .add_constraint(pumpkin_solver::equals(terms, 0, channel))
            .post();
    }

    // plays[p][i] is true when player p plays in the piece rehearsed in slot i.
    // It is exactly the "or" of slot_has[i][q] over the pieces q that p plays in.
    let plays_tag = solver.new_constraint_tag();
    let plays: Vec<Vec<Lit>> = (0..num_players)
        .map(|p| {
            (0..n)
                .map(|i| {
                    let lit = solver.new_literal();
                    let mut some_piece: Vec<Lit> = vec![!lit];
                    for q in 0..n {
                        if rehearsal[p][q] == 1 {
                            post_clause(solver, vec![!slot_has[i][q], lit], plays_tag);
                            some_piece.push(slot_has[i][q]);
                        }
                    }
                    post_clause(solver, some_piece, plays_tag);
                    lit
                })
                .collect()
        })
        .collect();

    // A player is present from the first slot they play in to the last. In slot
    // i they have arrived if they play in slot i or earlier (arrived[p][i]), and
    // have not yet left if they play in slot i or later (not_left[p][i]). Both
    // are only forced upwards: a larger value can only add waiting time, so the
    // minimisation settles on the exact "played at or before / at or after".
    let presence = solver.new_constraint_tag();
    let arrived: Vec<Vec<Lit>> = (0..num_players)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();
    let not_left: Vec<Vec<Lit>> = (0..num_players)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();
    for p in 0..num_players {
        for i in 0..n {
            post_clause(solver, vec![!plays[p][i], arrived[p][i]], presence);
            post_clause(solver, vec![!plays[p][i], not_left[p][i]], presence);
            if i > 0 {
                post_clause(solver, vec![!arrived[p][i - 1], arrived[p][i]], presence);
            }
            if i + 1 < n {
                post_clause(solver, vec![!not_left[p][i + 1], not_left[p][i]], presence);
            }
        }
    }

    // waits[p][q] is true when player p waits during piece q: p is present in the
    // slot where q is rehearsed but does not play in it. Waiting costs the
    // duration of the piece. waits is forced true in that situation and nothing
    // forces it true otherwise, so the minimisation keeps it exact.
    let waiting = solver.new_constraint_tag();
    let waits: Vec<Vec<Lit>> = (0..num_players)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();
    for p in 0..num_players {
        for i in 0..n {
            for q in 0..n {
                post_clause(
                    solver,
                    vec![!arrived[p][i], !not_left[p][i], plays[p][i], !slot_has[i][q], waits[p][q]],
                    waiting,
                );
            }
        }
    }

    // total waiting time = sum over players and pieces of duration[q] * waits[p][q].
    // The upper bound is every player waiting through every piece. Pieces of
    // duration 0 are left out of the sum because Pumpkin cannot take a zero weight.
    let longest_wait: i32 = duration.iter().sum::<i32>() * num_players as i32;
    let total_waiting = solver.new_bounded_integer(0, longest_wait.max(0));
    let mut weights: Vec<i32> = Vec::new();
    let mut lits: Vec<Lit> = Vec::new();
    for p in 0..num_players {
        for q in 0..n {
            if duration[q] != 0 {
                weights.push(duration[q]);
                lits.push(waits[p][q]);
            }
        }
    }
    let cost = solver.new_constraint_tag();
    if lits.is_empty() {
        solver
            .add_constraint(pumpkin_solver::equals(vec![total_waiting.scaled(1)], 0, cost))
            .post();
    } else {
        solver
            .add_constraint(pumpkin_solver::boolean_equals(weights, lits, total_waiting, cost))
            .post();
    }

    let mut m = Model::new();
    m.put("rehearsal_order", rehearsal_order);
    m.minimise(total_waiting);
    m
}
