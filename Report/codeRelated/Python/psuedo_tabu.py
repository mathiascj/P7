def tabu_search(modules, recipes, transport, iter, max_short_size):
	short_mem = []
	long_mem = []
	dynamic_mem = {}
	
	# Get initial liniear lines and evalutate them
	init_configs = get_init_configs(modules, recipes)
	for config in init_configs:
		evaluate(config, dynamic_mem)
		long_mem.append(config)

	frontier = best(long_mem)

	# The actual Tabu Search
	from 0 to iter:
		# Select what kind of neighbours we based on a heuristic
		func = get_neighbour_func()
		
		# Get neighbour and evaluate
		neighbours = func(modules, recipe, transport)
		for c in neighbours:
			evaluate(c)
			
		# Select the best neighbour not in short_mem
		frontier = best(neighbours - short_mem)
		
		# If all neighbours are in short_mem
		if frontier == None:  
			# We go to some config in long_mem
			frontier = backtrack(long_mem)
			long_mem.remove(frontier)
		
		# Update memory
		if len(short_mem) > max_short_size:
			short_mem.pop()
		short_mem.append(c)
		long_mem.append(c)
		
	return best(dynamic)

