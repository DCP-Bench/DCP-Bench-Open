# plan: flow_free_game

Board of 5x5 cells, colours 1..5 (each colour has two given endpoint cells)
-> cell[i] in 1..5, given cells fixed to their colour (m.intVar(v))
Connect matching colours with a pipe: the cells of one colour form one path between its two endpoints
-> per colour k: each endpoint has exactly one neighbour of colour k; every other cell of colour k has exactly two (m.sum(nb, "=", 1 or 2), under m.ifThen)
Connected (no loose cycle or detached piece): the pipe is grown from the first endpoint
-> per colour k: hop distance dist[k][i] in 0..24, start endpoint dist 0, other cells of colour k dist >= 1 and have a neighbour of colour k one step closer (witness BoolVars with m.reifyXeqYC)
Pipes do not cross or overlap: each cell holds one colour
-> one IntVar per cell (structural)
Cover the entire board: every cell gets a colour
-> cell domains are 1..5, no empty cells
Print the board B as a list of lists of colours
-> out.put("B", cell as IntVar[][])
objective: none (satisfaction)
