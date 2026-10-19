// Jobs puzzle: four people (0-3) hold eight different jobs, and each person holds
// exactly two jobs. Each job is held by one person; the output is the person index
// for each job.

const CHEF: usize = 0;
const NURSE: usize = 2;
const CLERK: usize = 3;
const POLICE: usize = 4;
const TEACHER: usize = 5;
const BOXER: usize = 7;

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let names = [
        "chef",
        "guard",
        "nurse",
        "clerk",
        "police_officer",
        "teacher",
        "actor",
        "boxer",
    ];
    let jobs: Vec<IntVar> = (0..8).map(|_| IntVar::new(0..=3)).collect();

    // held[j][p]: job j is held by person p.
    let mut held: Vec<Vec<Lit>> = Vec::new();
    for j in 0..8 {
        let mut row = Vec::new();
        for p in 0..4i64 {
            let b = jobs[j].equals(s, p)?;
            row.push(lit_of(s, b)?);
        }
        held.push(row);
    }

    // Each person holds exactly two jobs.
    for p in 0..4 {
        let mut e = LinExp::default();
        for j in 0..8 {
            e += bx(BoolVal::Lit(held[j][p]));
        }
        post(s, e, Comparator::Equal, 2)?;
    }

    // Clue 1: The nurse is not a teacher, police officer, or clerk.
    for &j in &[TEACHER, POLICE, CLERK] {
        for p in 0..4 {
            s.add_clause([!held[NURSE][p], !held[j][p]])?;
        }
    }

    // Clue 2: The clerk is not the chef.
    for p in 0..4 {
        s.add_clause([!held[CLERK][p], !held[CHEF][p]])?;
    }

    // Clue 3: Person 0 is not the boxer.
    s.add_clause([!held[BOXER][0]])?;

    // Clue 4: Person 3 is not the teacher, police officer, or nurse.
    for &j in &[TEACHER, POLICE, NURSE] {
        s.add_clause([!held[j][3]])?;
    }

    // Clue 5: Person 0, the chef, and the police officer went golfing together.
    s.add_clause([held[CHEF][0]])?;
    s.add_clause([held[POLICE][0]])?;

    let mut out = Out::new();
    for (j, name) in names.iter().enumerate() {
        out.put(name, &jobs[j]);
    }
    Ok(out)
}
