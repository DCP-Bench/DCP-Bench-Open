Assign a different colour to each of six countries (Belgium, Denmark, France, Germany, Netherlands, Luxembourg).
  -> colors = intVarArray 6, domain 1..6 (colours start at 1)
Two neighbouring countries cannot have the same colour.
  -> for each edge (a, b) in the instance graph (1-based country ids): colors[a-1] != colors[b-1]
Find a colouring that minimizes the number of colours used.
  -> colours are numbered 1..k, so the number of colours used is the largest colour: nb = max(colors), objective MINIMIZE nb (nValues gave suboptimal_solution)
Print the colour assigned to each country as a list (colors) of 6 integers.
  -> declared output "colors" = IntVar[6]
