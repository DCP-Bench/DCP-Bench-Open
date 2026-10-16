appointment_scheduling plan
schedule 4 people into 4 interview slots -> x[person][slot] Boolean matrix, n x n with n = number of people = number of slots
each person is assigned to exactly one slot -> for each person i: sum over j of x[i][j] = 1
each slot holds exactly one person -> for each slot j: sum over i of x[i][j] = 1
a person can only take a slot they are free in (m[i][j] = 1 means free) -> x[i][j] = 0 where m[i][j] = 0
objective: none (satisfaction)
