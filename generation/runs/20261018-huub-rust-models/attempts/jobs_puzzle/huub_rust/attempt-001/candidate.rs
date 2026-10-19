// Jobs puzzle: four people (0-3) hold eight different jobs, each person holds exactly two.
// Each job variable holds the index of the person who has that job.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Four people hold eight different jobs. Each person holds exactly two jobs.
    // The jobs are: chef, guard, nurse, clerk, police officer, teacher, actor, and boxer.
    let chef = m.new_int_decision(0..=3);
    let guard = m.new_int_decision(0..=3);
    let nurse = m.new_int_decision(0..=3);
    let clerk = m.new_int_decision(0..=3);
    let police = m.new_int_decision(0..=3);
    let teacher = m.new_int_decision(0..=3);
    let actor = m.new_int_decision(0..=3);
    let boxer = m.new_int_decision(0..=3);
    let jobs = vec![chef, guard, nurse, clerk, police, teacher, actor, boxer];

    // Each person holds exactly two jobs.
    for p in 0..4 {
        m.linear(count_eq(&jobs, p)).eq(2).post()?;
    }

    // Clues:
    // 1. The nurse is not a teacher, police officer, or clerk.
    m.linear(nurse - teacher).ne(0).post()?;
    m.linear(nurse - police).ne(0).post()?;
    m.linear(nurse - clerk).ne(0).post()?;

    // 2. The clerk is not the chef.
    m.linear(clerk - chef).ne(0).post()?;

    // 3. Person 0 is not the boxer.
    m.linear(boxer).ne(0).post()?;

    // 4. Person 3 is not the teacher, police officer, or nurse.
    m.linear(teacher).ne(3).post()?;
    m.linear(police).ne(3).post()?;
    m.linear(nurse).ne(3).post()?;

    // 5. Person 0, the chef, and the police officer went golfing together.
    // These are three different people, so person 0 is neither the chef nor the police officer,
    // and the chef and the police officer are different people.
    m.linear(chef).ne(0).post()?;
    m.linear(police).ne(0).post()?;
    m.linear(chef - police).ne(0).post()?;

    let mut out = Out::new();
    out.put("actor", actor)
        .put("boxer", boxer)
        .put("chef", chef)
        .put("clerk", clerk)
        .put("guard", guard)
        .put("nurse", nurse)
        .put("police_officer", police)
        .put("teacher", teacher);
    Ok(out)
}
