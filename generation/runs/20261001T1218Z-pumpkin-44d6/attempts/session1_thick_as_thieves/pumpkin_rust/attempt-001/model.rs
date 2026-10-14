// Thick as thieves: six suspects, at most two of them guilty (the getaway car
// held two). The innocent tell the truth and the guilty lie, so each suspect is
// guilty exactly when their statement is false. Who is guilty?
//
// The instance has no fields: the suspects and their statements are the
// puzzle's own data, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    // Each literal is true when that suspect is guilty.
    let artie = solver.new_literal();
    let bill = solver.new_literal();
    let crackitt = solver.new_literal();
    let dodgy = solver.new_literal();
    let edgy = solver.new_literal();
    let fingers = solver.new_literal();
    let suspects = vec![artie, bill, crackitt, dodgy, edgy, fingers];

    // At most two are guilty, because the getaway car was small. guilty counts them.
    let guilty = solver.new_bounded_integer(0, 2);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(vec![1; suspects.len()], suspects.clone(), guilty, tag))
        .post();

    // A suspect is guilty exactly when their statement is false.
    let statements = solver.new_constraint_tag();
    // Artie: "It wasn't me." and Crackitt: "No I wasn't." Each is false exactly
    // when the speaker is guilty, so these two statements constrain nothing.
    // Bill: "Crackitt was in it up to his neck." Bill is guilty iff Crackitt is not.
    solver.add_constraint(pumpkin_solver::clause(vec![bill, crackitt], statements)).post();
    solver.add_constraint(pumpkin_solver::clause(vec![!bill, !crackitt], statements)).post();
    // Dodgy: "If Crackitt did it, Bill did it with him." It is false exactly when
    // Crackitt is guilty and Bill is not: dodgy <-> (crackitt and not bill).
    solver.add_constraint(pumpkin_solver::clause(vec![!dodgy, crackitt], statements)).post();
    solver.add_constraint(pumpkin_solver::clause(vec![!dodgy, !bill], statements)).post();
    solver.add_constraint(pumpkin_solver::clause(vec![dodgy, !crackitt, bill], statements)).post();
    // Edgy: "Nobody did it alone", i.e. more than one is guilty. It is false
    // exactly when at most one is guilty: edgy <-> guilty <= 1.
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(vec![guilty], 1, statements))
        .reify(edgy);
    // Fingers: "It was Artie and Dodgy together." Fingers is guilty iff not both
    // Artie and Dodgy are: fingers <-> not (artie and dodgy).
    solver.add_constraint(pumpkin_solver::clause(vec![fingers, artie], statements)).post();
    solver.add_constraint(pumpkin_solver::clause(vec![fingers, dodgy], statements)).post();
    solver.add_constraint(pumpkin_solver::clause(vec![!fingers, !artie, !dodgy], statements)).post();

    let mut m = Model::new();
    m.put("artie", artie);
    m.put("bill", bill);
    m.put("crackitt", crackitt);
    m.put("dodgy", dodgy);
    m.put("edgy", edgy);
    m.put("fingers", fingers);
    m
}
