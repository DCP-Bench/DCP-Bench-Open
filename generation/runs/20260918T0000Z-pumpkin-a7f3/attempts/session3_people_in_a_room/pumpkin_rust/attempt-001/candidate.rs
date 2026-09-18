// Order thirteen arrivals so the room is never more than 7 women to 3 men.
// The head counts are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let total_people = 13;
    let num_males = 4;

    // true is a woman, false a man
    let sequence = cp.bools(total_people);
    cp.exactly(&sequence, total_people as i32 - num_males);

    // After i arrivals: 3 * women <= 7 * men, with men = i - women, so
    // 3 * women <= 7 * (i - women), i.e. 10 * women <= 7 * i.
    for i in 1..total_people {
        let prefix: Vec<Lit> = sequence[..i].to_vec();
        let tens = vec![10; prefix.len()];
        cp.bool_le(&tens, &prefix, 7 * i as i32);
    }

    let mut m = Model::new();
    m.put("sequence", sequence);
    m
}
