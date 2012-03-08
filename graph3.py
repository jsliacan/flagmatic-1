"""

flagmatic 2

Copyright (c) 2012, E. R. Vaughan. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1) Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2) Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

def graph_to_string (g):
	"""
	Returns a string representation of a 3-graph g in Flagmatic notation.
	g can have degenerate edges.
	
	EXAMPLES::

		sage: g = string_to_graph("4:123124")
		sage: g
		(4, ((1, 2, 3), (1, 2, 4)))
	
	"""
	s = "%d:" % g[0]
	for e in g[1]:
		s += "%d%d%d" % e
	return s


# TODO: Sanity checking, e.g. that edges do not contain vertices
# that do not belong to the graph, e.g. (4, (1, 5, 6))

def string_to_graph (s):
	"""
	Converts a string representation of a 3-graph s in Flagmatic notation 
	into a 3-graph g. g can have degenerate edges.

	EXAMPLES:

		sage: g = (4,((1,2,3),(1,2,4)))
		sage: graph_to_string(g)
		'4:123124'
		sage: g = (4,((1,1,1),(1,2,2)))
		sage: graph_to_string(g)
		'4:111122'

	"""
	if s[1] != ":":
		return None
	n = int(s[0])
	if n < 0 or n > 9:
		return None
	e = len(s) - 2
	if e == 0:
		return (n, ())
	if e % 3 != 0:
		return None
	m = e / 3
	edges = []
	for i in range(0, m):
		x = int(s[(3 * i) + 2]) # N.B. +2 because of n: header
		if x < 1 or x > n:
			return None
		y = int(s[(3 * i) + 3])
		if y < 1 or y > n:
			return None
		z = int(s[(3 * i) + 4])
		if z < 1 or z > n:
			return None
		edges.append((x, y, z))
		
	return (n, tuple(edges))


# TODO: Take into account degenerate edges?

def degrees(g):
	"""
	Returns a list consisting of the degrees of the vertices of g. Not intended for
	degenerate graphs.
	
	EXAMPLES:
	
	sage: g = (5,((1,2,3),(1,2,4),(1,3,4)))
	sage: degrees(g)
	[3, 2, 2, 2, 0]
	
	"""
	n = g[0]
	edges = g[1]
	return [len([e for e in edges if x in e]) for x in range(1, n + 1)]


def edge_density(g):
	"""
	Returns the edge density. If g has n vertices, it returns the number
	of edges divided by binomial(n, 3).
	"""
	return len(g[1]) / binomial(g[0], 3)


def subgraph_density(g, h):
	"""
	Returns the H-density of G. That is, if G has n vertices, and H has k
	vertices, it returns the number of k-sets of vertices of G that induce
	graphs isomorphic to H, divided by binomial(n, k).
	"""
	
	found, total = 0, 0
	
	for hv in Combinations(range(1, g[0] + 1), h[0]):
		if h == minimal_isomorph(induced_subgraph(g, hv), (0,())):
			found += 1
		total += 1

	return Integer(found) / total
	

# TODO: implement a forbidden_induced_edge_numbers.
# TODO: turn some forbidden graphs into forbidden edge numbers.


def generate_flags(n, tg, forbidden_edge_numbers={}, forbidden_graphs = [], forbidden_induced_graphs=[]):
	"""
	For an integer n, and a type tg, returns a list of all tg-flags on n
	vertices, that satisfy certain constraints.
	
	forbidden_edge_numbers should be a dictionary whose keys and values are integers,
	where an item (k, v) specifies that k-sets are to span fewer than v edges.
		
	forbidden_graphs should be a list of graphs that are forbidden as subgraphs.
	
	forbidden_induced_subgraphs should be a list of graphs that are forbidden as
	_induced_ subgraphs.
	
	EXAMPLES:
	
		sage: tg = (1,())
		sage: generate_flags(4, tg, forbidden_edge_numbers={4:2})
		[(4, ()), (4, ((2, 3, 4),)), (4, ((1, 2, 3),))]
	
	"""

	s = tg.n

	if n < s:
		return []

	if n == s:
		ntg = tg.copy()
		ntg.type = tg
		return [ntg]

	max_ne = (n - 1) * (n - 2) / 2
	max_e = n * max_ne / 3
	
	new_graphs = []
	hashes = set()
	
	smaller_graphs = generate_flags(n - 1, tg, forbidden_edge_numbers=forbidden_edge_numbers,
		forbidden_graphs=forbidden_graphs, forbidden_induced_graphs=forbidden_induced_graphs)
	
	possible_nbrs = Combinations(range(1, n), 2)

	for sg in smaller_graphs:
	
		pe = sg.ne
		ds = sg.degrees()
		maxd = max(ds[s:] + (0,))
			
		for ne in range(maxd, max_ne + 1):
		
			for nb in Combinations(possible_nbrs, ne):
			
				ng = sg.copy()
				ng.n = n
				for v in nb:
					ng.add_edge((v[0], v[1], n))

				if ng.has_forbidden_edge_numbers(forbidden_edge_numbers, must_have_highest=True):
					continue

				if ng.has_forbidden_graphs(forbidden_graphs, must_have_highest=True):
					continue

				if ng.has_forbidden_graphs(forbidden_induced_graphs, must_have_highest=True, induced=True):
					continue

				ng.make_minimal_isomorph()
				ng_hash = hash(ng)
				if not ng_hash in hashes:
					new_graphs.append(ng)
					hashes.add(ng_hash)

	return new_graphs


def generate_graphs(n, forbidden_edge_numbers={}, forbidden_graphs = [], forbidden_induced_graphs=[]):
	"""
	For an integer n, return a list of all 3-graphs on n vertices that satisfy certain
	constraints.
	
	forbidden_edge_numbers should be a dictionary whose keys and values are integers,
	where an item (k, v) specifies that k-sets are to span fewer than v edges.
		
	forbidden_graphs should be a list of graphs that are forbidden as subgraphs.
	
	forbidden_induced_subgraphs should be a list of graphs that are forbidden as
	_induced_ subgraphs.
	
	EXAMPLES:
	
		sage: generate_graphs(4, forbidden_edge_numbers={4:3})
		[(4, ()), (4, ((1, 2, 3),)), (4, ((1, 2, 3), (1, 2, 4)))]
	
	"""
	tg = flagmatic_flag()
	return generate_flags(n, tg, forbidden_edge_numbers=forbidden_edge_numbers,
		forbidden_graphs=forbidden_graphs, forbidden_induced_graphs=forbidden_induced_graphs)


def flag_orbits(tg, flags):
	"""
	flags should be a list of flags of the type tg. Returns a list of tuples.
	Each tuple contains the indices of the flags that are in the same orbit
	under the action of relabelling the vertices of tg.
	"""
	s = tg.n
	min_flags = []

	for fg in flags:
		mfgs = str(fg)
		for perm in Permutations(range(1, s + 1)):
			permplus = perm + range(s + 1, fg.n + 1)
			ntg = tg.copy()
			ntg.relabel(perm)
			nfg = fg.copy()
			nfg.relabel(permplus)
			nfg.type = ntg
			nfg.make_minimal_isomorph()
			nfgs = str(nfg)
			if nfgs < mfgs:
				mfgs = nfgs
		min_flags.append(mfgs)

	orbs = []
	for mfgs in set(min_flags):
		orbs.append(tuple([i for i in range(len(min_flags)) if min_flags[i] == mfgs]))

	return sorted(orbs)


from sage.modules.misc import gram_schmidt

def flag_basis(tg, flags, orthogonalize=True):
	"""
	flags should be a list of flags of the type tg. Returns a basis for the flags
	that is a block matrix of two blocks. Uses flag orbits to create invariant-
	anti-invariant decomposition. If orthogonalize=True, perform Gram-Schmidt
	orthogonalization.
	"""
	
	orbs = flag_orbits(tg, flags)
	
	Inv = matrix(QQ, len(orbs), len(flags), sparse=True)
	row = 0
	for orb in orbs:
		for j in orb:
			Inv[row, j] = 1
		row += 1
	
	# There might be no anti-invariant part.
	if len(orbs) == len(flags):
		return Inv
	
	AntiInv = matrix(QQ, len(flags) - len(orbs), len(flags), sparse=True)
	row = 0
	for orb in orbs:
		for j in orb[1:]:
			AntiInv[row, orb[0]] = 1
			AntiInv[row, j] = -1
			row += 1

	sys.stdout.write("Invariant-AntiInvariant: %d + %d = %d\n" % (Inv.nrows(), AntiInv.nrows(),
		len(flags)))
	
	if orthogonalize:
	
		# Note: the following does not preserve sparsity
		#AntiInv, mu = AntiInv.gram_schmidt()
	
		AntiInvRows, mu = gram_schmidt(AntiInv.rows())
		AntiInv = matrix(QQ, AntiInvRows, sparse=True)

	return block_matrix([[Inv],[AntiInv]])


# Deprecated: use flag_products instead

def slow_flag_products (g, s, m, typs, flags):

	n = g[0]

	vertices = range(1, n + 1)

	num_typs = len(typs)
	num_flags = [len(fl) for fl in flags]
	
	#pair_densities = dict(((i, j, k), 0) for i in range(num_typs)
	#	for j in range(num_flags[i]) for k in range(num_flags[i]))
	pair_densities = {}
	
	for tv in Permutations(vertices, s):
	
		tg = induced_subgraph(g, tv)
		
		if not tg in typs:
			continue
		
		tindex = typs.index(tg)
	
		non_typ_verts = [x for x in vertices if not x in tv]
	
		for fav in Combinations(non_typ_verts, m - s):

			fag = minimal_isomorph(induced_subgraph(g, tv + fav), tg)
			faindex = flags[tindex].index(fag)
			
			remaining_verts = [x for x in non_typ_verts if not x in fav]
			
			for fbv in Combinations(remaining_verts, m - s):

				fbg = minimal_isomorph(induced_subgraph(g, tv + fbv), tg)
				fbindex = flags[tindex].index(fbg)
				
				key = (tindex, faindex, fbindex)
				pair_densities[key] = pair_densities.setdefault(key, 0) + 1

	total = falling_factorial(n, s) * binomial(n - s, m - s) * binomial(n - m, m - s)

	for key in pair_densities.iterkeys():
		pair_densities[key] = Integer(pair_densities[key]) / total

	return pair_densities


# def induced_subgraph (g, S):
# 
# 	good_edges = [e for e in g[1] if all(x in S for x in e)]
# 	p = [0 for i in range(g[0] + 1)]
# 	for i in range(len(S)):
# 		p[S[i]] = i + 1
# 
# 	edges = sorted([tuple(sorted([p[x] for x in e])) for e in good_edges])
# 
# 	return (len(S), tuple(edges))

def split_vertex (g, x):

	n = g[0]
	new_edges = []
	for e in g[1]:
		le = list(e)
		if le.count(x) == 1:
			nle = [y for y in le if y != x]
			new_edges.append(tuple(nle + [n + 1]))
		elif le.count(x) == 2:
			nle = [y for y in le if y != x]
			new_edges.append(tuple(nle + [x, n + 1]))
			new_edges.append(tuple(nle + [n + 1, n + 1]))
		elif le.count(x) == 3:
			new_edges.append((x, x, n + 1))
			new_edges.append((x, n + 1, n + 1))
			new_edges.append((n + 1, n + 1, n + 1))
	return (n + 1, g[1] + tuple(new_edges))

def delete_improper_edges (g):
	edges = [e for e in g[1] if len(frozenset(e)) == 3]
	return (g[0], tuple(edges))

# Allows repeated vertices...

def induced_subgraph (g, S):

	vertices = []
	for x in S:
		if not x in vertices:
			vertices.append(x)
		else:
			g = split_vertex(g, x)
			vertices.append(g[0])
	vertex_set = frozenset(vertices)
	good_edges = tuple(e for e in g[1] if frozenset(e) <= vertex_set)
	p = [0 for i in range(g[0] + 1)]
	for i in range(len(vertices)):
		x = vertices[i]
		p[x] = i + 1
	edges = tuple(sorted([tuple(sorted([p[x] for x in e]))
		for e in good_edges]))

	ig = (len(vertex_set), edges)

	return delete_improper_edges(ig)



# TODO: this function remains, as it handles degenerate graphs.

def degenerate_minimal_isomorph (g, t=(0,())):
	
	s = t[0]
	n = g[0]
	min_edges = g[1]
	
	for p in Permutations(range(s + 1, n + 1), n - s):
		
		pt = tuple(range(1, s + 1)) + tuple(p)
		edges = tuple(sorted([tuple(sorted([pt[e[i] - 1] for i in range(3)]))
			for e in g[1]]))
		
		if edges < min_edges:
			min_edges = edges
			
	return (n, min_edges)


def asymptotic_flag_density_fixed (g, t, f, tv):

	s = t[0]
	m = f[0]
	n = g[0]
	count = 0
	total = 0

	# TODO: rewrite to use UnorderedTuple
	
	for pf in Tuples(range(1, n + 1), m - s):
		
		p = tv + pf
		
		total += 1
		it = induced_subgraph(g, p[:s])
		if it == t:
			ig = induced_subgraph(g, p)
			if f == degenerate_minimal_isomorph(ig, t):
				count += 1
	
	return Integer(count) / total


def sparse_symm_matrix_to_compact_repr(M):

	ed = {}
	for key, value in M.dict().iteritems():
		x, y = key
		if x <= y:
			ed[key] = repr(value)

	d = {
		"n" : M.nrows(),
		"blocks" : M.subdivisions()[0],
		"entries" : ed
	}

	return repr(d)
	

def sparse_symm_matrix_from_compact_repr(ds):

	d = eval(ds)
	n = d["n"]
	M = matrix(QQ, n, n, sparse=True)
	for key, value in d["entries"].iteritems():
		x, y = key
		M[x, y] = sage_eval(value)
		M[y, x] = M[x, y]
	M.subdivide(d["blocks"], d["blocks"])
	return M
	