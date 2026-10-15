# crew plan

Assign 20 flight attendants to 10 flights; each flight needs a crew size, stewards, hostesses and speakers of French, Spanish, German.
-> x[f][p] Bool per flight and person; crew size is a PB sum over the flight: sum_p x[f][p] == required[f][0].

Each flight needs a certain number of cabin crew.
-> sum_p x[f][p] == required_crew[f][0]

Each flight needs a certain number of stewards (at least, the required count of steward-attendants).
-> sum_{p steward} x[f][p] >= required_crew[f][1]

Each flight needs a certain number of hostesses (at least).
-> sum_{p hostess} x[f][p] >= required_crew[f][2]

They have to speak certain languages: French, Spanish, German speakers at least the required count per flight.
-> sum_{p speaks L} x[f][p] >= required_crew[f][3 + k] for L in French, Spanish, German

Every cabin crew member has two flights off after an attended flight.
-> for each person p and each window of three consecutive flights: sum over the window of x[f][p] <= 1 (no two flights within distance two).

Objective: none (satisfaction). Output crew[f][p] = x[f][p].
