Problem: added_corners. Circles (corners) and squares (edge cells) of a 3x3 frame get digits 1..8, each once. Each square equals the sum of its two adjoining circles.
Positions in reading order: TL, TM, TR, ML, MR, BL, BM, BR (positions[0..7]).
Enter the digits 1 through 8 in the circles and squares -> allDifferent over all 8 positions, domain 1..8, "AC".
Each square equals the sum of the numbers in the adjoining circles:
  top square TM = TL + TR -> expression TL.add(TR).eq(TM).post()
  middle-left square ML = TL + BL -> TL.add(BL).eq(ML).post()
  middle-right square MR = TR + BR -> TR.add(BR).eq(MR).post()
  bottom square BM = BL + BR -> BL.add(BR).eq(BM).post()
Objective: none (satisfaction). Output positions in reading order.
