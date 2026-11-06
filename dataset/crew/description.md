Assign flight attendants to flights. Each flight needs a certain number of cabin crew, and they have to speak certain languages.

`attributes[p]` describes person p as five 0/1 values: steward, hostess, speaks French, speaks Spanish, speaks German.
`required_crew[f]` describes flight f as six numbers: the number of cabin crew, then the numbers of stewards, hostesses,
French speakers, Spanish speakers and German speakers needed. A flight has exactly that number of cabin crew, and at least
the required number of each of the others; one person can count towards several of them.

Every cabin crew member has at least two flights off after an attended flight, so nobody attends more than one of any three consecutive flights.

Print whether for each flight a person is assigned to it (crew) as a list of lists of 0/1 values, where crew[f][p] is 1 if person p is assigned to flight f, and 0 otherwise.
