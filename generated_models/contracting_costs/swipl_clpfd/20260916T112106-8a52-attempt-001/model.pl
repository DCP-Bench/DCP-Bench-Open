:- use_module(library(clpfd)).

% Contracting costs: six tradesmen, six pairwise bills.
model(_Instance, Vars,
      [paper_hanger-PaperHanger, painter-Painter, plumber-Plumber,
       electrician-Electrician, carpenter-Carpenter, mason-Mason]) :-
    Vars = [PaperHanger, Painter, Plumber, Electrician, Carpenter, Mason],
    Vars ins 1..5300,
    PaperHanger + Painter #= 1100,
    Painter + Plumber #= 1700,
    Plumber + Electrician #= 1100,
    Electrician + Carpenter #= 3300,
    Carpenter + Mason #= 5300,
    Mason + Painter #= 3200.
