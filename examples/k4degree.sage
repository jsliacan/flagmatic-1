P = ThreeGraphAxiomsProblem()
P.forbid_subgraph((4, 4))
P.generate_flags(6)
P.clear_densities()
P.add_degree_axiom(5/9, False)
P.add_equal_degrees_axiom(True)
C = BlowupConstruction(ThreeGraphFlag("3:112223331123"))
P.set_extremal_construction(C)
P.solve_sdp(True)
P.change_solution_bases()
P.make_exact(2^20)
P.check_exact_bound()