// Session 3 Exodus: five children (Bernice, Carl, Debby, Sammy, Ted) present five parts of the
// Exodus story. Each child has an age (3, 5, 7, 8 or 10), a family country (Ethiopia, Kazakhstan,
// Lithuania, Morocco or Yemen) and a story (burning bush, captivity, Moses's youth, Passover or
// the Ten Commandments). Output: four arrays of labels 1..5; equal labels mean the same association.

// Position of each label k+1 in an array of labels: arr[pos[k]] == k+1 for k in 0..5.
fn positions(m: &mut Model, arr: &[View<i64>]) -> Res<Vec<View<i64>>> {
    let mut pos = Vec::new();
    for k in 0..5i64 {
        let p = m.new_int_decision(0..=4);
        let v = m.element(arr.to_vec()).index(p).define();
        m.linear(v).eq(k + 1).post()?;
        pos.push(p);
    }
    Ok(pos)
}

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Labels of the children, ages, countries and stories (Bernice, Carl, Debby, Sammy, Ted).
    let children = m.new_int_decisions(5, 1..=5);
    let ages = m.new_int_decisions(5, 1..=5);
    let countries = m.new_int_decisions(5, 1..=5);
    let stories = m.new_int_decisions(5, 1..=5);

    // Each category uses the numbers 1 to 5 once, so each number links one child, age, country and story.
    m.unique(children.clone()).post()?;
    m.unique(ages.clone()).post()?;
    m.unique(countries.clone()).post()?;
    m.unique(stories.clone()).post()?;

    // The age of the association with label k+1, taken from the age slots 3, 5, 7, 8, 10.
    let age_pos = positions(m, &ages)?;
    let mut age_val = Vec::new();
    for &p in age_pos.iter() {
        let a = m.element(vec![3i64, 5, 7, 8, 10]).index(p).define();
        age_val.push(a);
    }

    // Debby's family is from Lithuania.
    eq2(m, countries[2] - children[2], 0)?;

    // The child who told the story of the Passover is two years older than Bernice.
    let passover_age = m.element(age_val.clone()).index(stories[3] - 1).define();
    let bernice_age = m.element(age_val.clone()).index(children[0] - 1).define();
    eq2(m, passover_age - bernice_age, 2)?;

    // The child whose family is from Yemen is younger than the child from the Ethiopian family.
    let yemen_age = m.element(age_val.clone()).index(countries[4] - 1).define();
    let ethiopia_age = m.element(age_val.clone()).index(countries[0] - 1).define();
    m.linear(yemen_age).lt(ethiopia_age).post()?;

    // The child from the Moroccan family is three years older than Ted.
    let morocco_age = m.element(age_val.clone()).index(countries[3] - 1).define();
    let ted_age = m.element(age_val.clone()).index(children[4] - 1).define();
    eq2(m, morocco_age - ted_age, 3)?;

    // Sammy is three years older than the child who told the story of Moses's youth in the house of the Pharaoh.
    let sammy_age = m.element(age_val.clone()).index(children[3] - 1).define();
    let youth_age = m.element(age_val.clone()).index(stories[2] - 1).define();
    eq2(m, sammy_age - youth_age, 3)?;

    let mut out = Out::new();
    out.put("ages", ages)
        .put("children", children)
        .put("countries", countries)
        .put("stories", stories);
    Ok(out)
}
