// Exodus puzzle (session3_exodus): five children Bernice, Carl, Debby, Sammy and Ted
// present different parts of the Exodus story. Each child has a different age (three,
// five, seven, eight or ten), a family country of origin (Ethiopia, Kazakhstan,
// Lithuania, Morocco or Yemen) and a story (burning bush, captivity, Moses's youth,
// Passover or the Ten Commandments). The instance has no fields.
//
// Indices: children 0 Bernice, 1 Carl, 2 Debby, 3 Sammy, 4 Ted.
// Ages: index a has the value AGE[a]. Countries: 0 Ethiopia, 1 Kazakhstan, 2 Lithuania,
// 3 Morocco, 4 Yemen. Stories: 0 burning bush, 1 captivity, 2 Moses's youth, 3 Passover,
// 4 Ten Commandments.
//
// Output numbers: the child (1..5) that has a given age, country or story. Child c is
// number c + 1, so children is 1..5.

const AGE: [i64; 5] = [3, 5, 7, 8, 10];

// Five-by-five Boolean matrix: m[child][value].
fn new_matrix(s: &mut Cadical) -> Vec<Vec<Lit>> {
    let mut m: Vec<Vec<Lit>> = Vec::new();
    for _ in 0..5 {
        let row: Vec<Lit> = (0..5).map(|_| s.new_lit()).collect();
        m.push(row);
    }
    m
}

// Each child has exactly one value, and each value belongs to exactly one child.
fn one_each(s: &mut Cadical, m: &[Vec<Lit>]) -> Res {
    for row in m {
        s.add_clause(row.clone())?;
        for i in 0..5 {
            for j in i + 1..5 {
                s.add_clause([!row[i].clone(), !row[j].clone()])?;
            }
        }
    }
    for v in 0..5 {
        let col: Vec<Lit> = (0..5).map(|c| m[c][v].clone()).collect();
        s.add_clause(col.clone())?;
        for i in 0..5 {
            for j in i + 1..5 {
                s.add_clause([!col[i].clone(), !col[j].clone()])?;
            }
        }
    }
    Ok(())
}

// If all conditions hold, the age of child x and the age of child y satisfy rel.
// Every pair of age indices that breaks rel gets a clause forbidding it.
fn age_rel(
    s: &mut Cadical,
    age: &[Vec<Lit>],
    conds: &[Lit],
    x: usize,
    y: usize,
    rel: fn(i64, i64) -> bool,
) -> Res {
    for i in 0..5 {
        for j in 0..5 {
            if !rel(AGE[i], AGE[j]) {
                let mut clause: Vec<Lit> = conds.iter().map(|l| !l.clone()).collect();
                clause.push(!age[x][i].clone());
                clause.push(!age[y][j].clone());
                s.add_clause(clause)?;
            }
        }
    }
    Ok(())
}

// Output k holds the child number (1..5) whose value in this attribute is k.
fn link(s: &mut Cadical, m: &[Vec<Lit>]) -> Res<Vec<IntVar>> {
    let mut vars: Vec<IntVar> = Vec::new();
    for k in 0..5 {
        let v = IntVar::new(1..=5);
        for c in 0..5 {
            post_if(s, &[m[c][k].clone()], iv(&v), Comparator::Equal, c as i64 + 1)?;
        }
        vars.push(v);
    }
    Ok(vars)
}

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let age = new_matrix(s);
    let country = new_matrix(s);
    let story = new_matrix(s);
    one_each(s, &age)?;
    one_each(s, &country)?;
    one_each(s, &story)?;

    // Debby's family is from Lithuania.
    s.add_clause([country[2][2].clone()])?;

    // The child who told the story of the Passover is two years older than Bernice.
    for c in 0..5 {
        age_rel(s, &age, &[story[c][3].clone()], c, 0, |x, y| x == y + 2)?;
    }

    // The child whose family is from Yemen is younger than the child from the Ethiopian family.
    for c in 0..5 {
        for d in 0..5 {
            age_rel(
                s,
                &age,
                &[country[c][4].clone(), country[d][0].clone()],
                c,
                d,
                |x, y| x < y,
            )?;
        }
    }

    // The child from the Moroccan family is three years older than Ted.
    for c in 0..5 {
        age_rel(s, &age, &[country[c][3].clone()], c, 4, |x, y| x == y + 3)?;
    }

    // Sammy is three years older than the child who told the story of Moses's youth in the house of the Pharaoh.
    for c in 0..5 {
        age_rel(s, &age, &[story[c][2].clone()], 3, c, |x, y| x == y + 3)?;
    }

    let ages_out = link(s, &age)?;
    let countries_out = link(s, &country)?;
    let stories_out = link(s, &story)?;
    let children: Vec<i64> = vec![1, 2, 3, 4, 5];

    let mut out = Out::new();
    out.put("ages", &ages_out)
        .put("children", &children)
        .put("countries", &countries_out)
        .put("stories", &stories_out);
    Ok(out)
}
