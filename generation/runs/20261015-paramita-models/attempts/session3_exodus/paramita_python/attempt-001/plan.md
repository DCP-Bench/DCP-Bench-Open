Five children, each a different age (three, five, seven, eight, or ten) -> one-hot age per child (age_c_v), sum over v == 1 per child, sum over c == 1 per v; integer age = sum(years[v] * age_c_v)
Each family from a different country (Ethiopia, Kazakhstan, Lithuania, Morocco, or Yemen) -> one-hot country per child (country_c_v), exactly one per child, each country once
Each child related a different part of the story (burning bush, captivity, Moses's youth, Passover, or the Ten Commandments) -> one-hot story per child (story_c_v), exactly one per child, each story once
Print children (children) as the child numbers 1..5 (Bernice=1 ... Ted=5) -> constant [1,2,3,4,5], row id of a child is its number
Print ages / countries / stories indexed by value: ages[j] = sum((c+1) * age_c_j) over children -> the child number holding age j; same for countries and stories
1. Debby's family is from Lithuania -> country_2_2 (unit constraint)
2. The child who told the story of the Passover is two years older than Bernice -> per child c: If(story_c_Passover, age_c == age_Bernice + 2)
3. The child whose family is from Yemen is younger than the child from the Ethiopian family -> per pair (c, d): If(country_c_Yemen & country_d_Ethiopia, age_c < age_d)
4. The child from the Moroccan family is three years older than Ted -> per child c: If(country_c_Morocco, age_c == age_Ted + 3)
5. Sammy is three years older than the child who told the story of Moses's youth -> per child c: If(story_c_MosesYouth, age_Sammy == age_c + 3)
Objective: none (satisfaction)
