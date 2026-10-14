# Plan: session3_exodus (rows 0..4, one row = one association; each category is a permutation of rows)
Each child, country, story and age gets the row of the association it belongs to -> distinct(*this, child/country/story/age, IPL_DOM)
Age of each row: age_at is the inverse of age (channel), years[r] = table of ages at age_at[r] -> channel(*this, age, age_at), element(*this, IntArgs({3,5,7,8,10}), age_at[r], years[r])
Debby's family is from Lithuania -> rel(*this, child[Debby] == country[Lithuania])
The child who told the story of the Passover is two years older than Bernice -> rel(years_of(story[Passover]) == years_of(child[Bernice]) + 2) -> element(*this, years, row, y)
The child whose family is from Yemen is younger than the child from the Ethiopian family -> rel(years_of(country[Yemen]) < years_of(country[Ethiopia])) -> element(years, row)
The child from the Moroccan family is three years older than Ted -> rel(years_of(country[Morocco]) == years_of(child[Ted]) + 3) -> element(years, row)
Sammy is three years older than the child who told the story of Moses's youth -> rel(years_of(child[Sammy]) == years_of(story[Moses's youth]) + 3) -> element(years, row)
Branching -> branch(child, INT_VAR_SIZE_MIN, INT_VAL_MIN), then country, story, age; age_at and years follow from channel and element
Objective -> none (satisfaction); outputs ages, children, countries, stories are the rows + 1 (1..5), via output arrays
