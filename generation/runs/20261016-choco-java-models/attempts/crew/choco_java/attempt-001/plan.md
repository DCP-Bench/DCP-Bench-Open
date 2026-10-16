Assign 20 flight attendants to 10 flights; each flight needs a number of cabin crew -> sum over persons of crew[f][p] = total_f (exact)
Each flight needs a certain number of cabin crew -> per flight, sum of crew[f][p] = required_crew[f][0]
Each flight needs stewards (role column) -> sum over stewards p of crew[f][p] >= required_crew[f][1]
Each flight needs hostesses (role column) -> sum over hostesses p of crew[f][p] >= required_crew[f][2]
they have to speak certain languages (French) -> sum over French speakers of crew[f][p] >= required_crew[f][3]
they have to speak certain languages (Spanish) -> sum over Spanish speakers of crew[f][p] >= required_crew[f][4]
they have to speak certain languages (German) -> sum over German speakers of crew[f][p] >= required_crew[f][5]
Every cabin crew member has two flights off after an attended flight -> for each person, flight f and f+1 not both attended; f and f+2 not both attended -> arithm(crew[f][p] + crew[f+d][p] <= 1), d = 1, 2
objective: none (satisfaction); output crew[f][p] as 0/1 booleans
