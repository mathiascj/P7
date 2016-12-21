tabu_search(modules, recipes, transport, iter):
	short = []
	long = []
	dynamic = {}

	init_configs = get_init_configs(modules, recipes)

	for c in init_configs:
		evaluate(c, dynamic)
		long.append(c)

	frontier = best(dynamic)

	from 0 to iter:
		func = get_neighbour_func()
		neighbours = func(modules, recipe, transport)
		for c in neighbours:
			evaluate(c)
			short.append(c)
			long.append(c)

	frontier = best(neighbours - short)
	if front = empty:
		front backtrack(long)

	return best(dynamic)

