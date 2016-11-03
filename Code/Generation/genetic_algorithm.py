import random
import bisect


def ff(config):
    return random.randint(1, 100)

p1 = {1: {2}, 2: {3, 4}, 3: {6}, 4: {5}, 5: {3}, 6: {0}}
p2 = {1: {2}, 2: {4}, 3: {6}, 4: {5}, 5: {6}, 6: {0}}
p3 = {1: {2}, 2: {3}, 3: {4}, 4: {5}, 5: {6}, 6: {0}}
p4 = {1: {2, 3, 4, 5, 6}, 2: {1}, 3: {1}, 4: {1}, 5: {1}, 6: {0}}

population = list(zip([p1, p2, p3, p4], [50, 60, 30, 70]))


def genetic_algorithm(start_population, number_of_generations, max_pop, fitness_func):
    """
    :param start_population: The initial population, doesn't have to be equal to max_pop. A population is a list of
    tuples, where the first element of the tuple is a configuration and the second a fitness.
        ex. [({1: {2}, 2: {1}}, 20),
             ({1: {2}, 2: {3}, 3: {1}}, 10)]
    :param number_of_generations: A number indicating for how many generations the GA will run for
    :param max_pop: An integer indicating the maximum amount of individuals in a population
    :param fitness_func: A function that can find the fitness of a configuration, should take one parameter, a
    configuration
    :return: A tuple containing the best configuration it could find and the associated fitness value
    """
    population = start_population

    for i in range(number_of_generations * max_pop):
        # TODO: Perhaps make it so that we can't breed non-working children
        print('Copulation #' + str(i))

        mom, dad = selection(population)
        child = crossover(mom, dad)

        # MUTATIONS
        mutation_chance(mutation_add_connection, child, 30)
        mutation_chance(mutation_remove_connection, child, 30)
        mutation_chance(mutation_swap_modules, child, 10)

        cfit = fitness_func(child)

        # Kill individuals if our population is too big
        while len(population) > max_pop:
            kill_individual(population)

        population.append((child, cfit)) # Add the new child to the population

    result = min(population, key=lambda item: item[1])
    return result


def selection(population):
    """
    :param population: The population from which we select 2 individuals. See genetic_algorithm for more
    :return: 2 distinct configurations from the populations selected by weighted_choice
    """
    weighted_pop = get_weighted_population(population, inverse=True)

    mom, w1, i1 = weighted_choice(weighted_pop)
    weighted_pop.remove((mom, w1))  # We remove mom from the weighted population so we can't select her again
    dad, w2, i2 = weighted_choice(weighted_pop)

    return mom, dad


def crossover(mom, dad):
    """
    :param mom: First parent used for crossover
    :param dad: Second parent used for the crossover, should be different from mom
    :return: Returns a child that is the result of a crossover between mom and dad
    """
    # TODO: Maybe revamp so it can't return useless children
    # TODO: Right now we can only cross over on parents of same length

    child = {}
    for i in range(1, len(mom) + 1):
        choice = random.choice([0, 0, 1, 1, 2])
        if choice == 0:
            child[i] = mom[i]
        elif choice == 1:
            child[i] = dad[i]
        else:
            child[i] = mom[i] | dad[i]
    return child


def kill_individual(population):
    """
    SIDE EFFECT: Changes the population it recieves as input
    :param population: The population from which an individual will be removed
    :return: The population but with the removed individual
    """
    # TODO: Maybe don't return, due to the side effect doing the job already

    weighted_pop = get_weighted_population(population, inverse=False)
    p, w, i = weighted_choice(weighted_pop)
    population.remove(population[i])

    return population


def mutation_chance(mutation_func, child, permille):
    """
    :param mutation_func: A mutation functions, which will be called with permille chance
    :param child: The child that will be fed to the mutation function
    :param permille: The permille, with which chance the mutation function will be run
    """
    x = random.randint(0, 1000)
    if x < permille:
        mutation_func(child)


def mutation_swap_modules(configuration):
    """ Swaps the values of two keys in a dict. This represents swapping two modules with each other
    SIDE EFFECT: edits the configuration paramter
    :param configuration: A configuration in the form of a dictionary, where the keys are integers and the values are
    a set of integers.
        ex. {1: {2, 3}, 2: {0}, 3: {0}}
    :return: The changed configuration
    """
    keys = list(configuration.keys())
    k1 = random.choice(keys)
    k2 = random.choice(keys)

    temp = configuration[k1]
    configuration[k1] = configuration[k2]
    configuration[k2] = temp

    return configuration


def mutation_add_connection(configuration):
    """ Adds a random integer that exists in set(keys) + {0}. This represents adding a random connection from one module
     to another.
    SIDE EFFECT: edits the configuration paramter
    :param configuration: A configuration in the form of a dictionary, where the keys are integers and the values are
    a set of integers.
        ex. {1: {2, 3}, 2: {0}, 3: {0}}
    :return: The changed configuration
    """
    keys = list(configuration.keys())
    k1 = random.choice(keys)    # TODO: If we can select 0 here, we might get infinite loop in the while later
    keys.append(0)              # So we can add a random connection to 0

    k2 = k1
    while k1 == k2:             # We keep going untill we find a different key.
        k2 = random.choice(keys)

    configuration[k1].add(k2)

    return configuration


def mutation_remove_connection(configuration):
    """ Removes a random integer from a value, but only if there exists more than 1. Represents removing a connection
    from one module to another.
    SIDE EFFECT: edits the configuration paramter
    :param configuration: A configuration in the form of a dictionary, where the keys are integers and the values are
    a set of integers.
        ex. {1: {2, 3}, 2: {0}, 3: {0}}
    :return: The changed configuration
    """
    keys = list(configuration.keys())
    k = random.choice(keys)

    if len(configuration[k]) > 1:
        values = configuration[k]
        v = random.choice(values)
        configuration[k].remove(v)

    return configuration


# Helping functions
def normalise(x, min, max):
    """ Normalises a value to be between 0 and 1
    :param x: Value you wish to normalise
    :param min: The minimum value
    :param max: The maximum value
    :return: The normalised value of x
    """
    if min != max:
        return (x - min) / (max - min)
    else:
        return 1


def weighted_choice(choices):
    """ Randomly picks a choices based on weights
    :param choices: A list of tuples, where the first element of the tuple is a potential choice and the second element
    is the weight with which the choice can be picked
    :return: A randomly weighted selection of a choice, along with its weight and the index it had.
    """
    values, weights = zip(*choices)
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random.random() * total
    i = bisect.bisect_left(cum_weights, x)
    return values[i], weights[i], i


def get_weighted_population(population, inverse=False):
    """ Makes a weighted population
    :param population: The population from which we get weights, genetic_algorithm for more
    :return: A list of tuples, where the first element of each tuple is an individual and the second the associated
    weight.
    """
    individuals, fits = zip(*population)
    min_fit = min(fits)
    max_fit = max(fits)

    if inverse:
        weights = [1 - normalise(fit, min_fit, max_fit) for fit in fits]
    else:
        weights = [normalise(fit, min_fit, max_fit) for fit in fits]

    weighted_population = list(zip(individuals, weights))

    return weighted_population