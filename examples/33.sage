P = GraphProblem(5, forbid_induced=(3,0), density=(3,3), minimize=True)
C = BlowupConstruction(GraphFlag("2:1122"), phantom_edge=[1,2])
P.set_extremal_construction(C)
P.solve_sdp()
P.make_exact()