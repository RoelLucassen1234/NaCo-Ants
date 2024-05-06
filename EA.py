import random
from Tests import Ant
from Environment import Environment

import math

ANT_POPULATION = 50
NUMBER_OF_MODELS = 10
GENERATION = 100
MUTATION_RATE = 0.1
EPSILON = 0.1
env = Environment(ANT_POPULATION, "")



def initiale_direction() -> float:
    # Generate a random angle between 0 and 2*pi
    angle = random.uniform(0, 2 * math.pi)
    # Adjust the angle to make the movement less jittery
    angle += random.uniform(-5, 5)
    return angle


def generate_initial_population(number_of_ants):

    population = []
    init_direction = []

    for i in range(number_of_ants):
        dir = initiale_direction()
        init_direction.append(dir)
        population.append(Ant(direction=dir))

    return population, init_direction



def run_environment(ants):
    return env.run_simulation(ants)

def select_parents(population):
    # Select two parents from the population using tournament selection
    parent1 = max(random.sample(population, k=5), key=lambda ant: ant.fitness)
    parent2 = max(random.sample(population, k=5), key=lambda ant: ant.fitness)
    return parent1, parent2

def crossover(parent1, parent2):
    # Perform crossover between two parents to create a child
    split_point = random.randint(1, len(parent1.path)-1)
    #TODO find a crossover value that we can use for EA, currently we have none
    child_path = parent1.path[:split_point] + parent2.path[split_point:]
    child = Ant(child_path)
    return child

 #TODO DEPENDS ON CROSSOVER
def mutate(ant):
    # Perform mutation on an ant's path
    new_path = ''
    for direction in ant.path:
        if random.random() < MUTATION_RATE:
            new_path += random.choice(['U', 'D', 'L', 'R'])
        else:
            new_path += direction
    mutated_ant = Ant(new_path)
    return mutated_ant

def get_fitness_sum(population):
    # Calculate the sum of the fitness values of all ants in the population
    fitness_sum = sum
    return fitness_sum

def run_generation(population):
    # Run a single generation of the genetic algorithm
    new_population = []
    for i in range(len(population)):
        parent1, parent2 = select_parents(population)
        child = crossover(parent1, parent2)
        if random.random() < MUTATION_RATE:
            child = mutate(child)
        # child.evaluate_fitness()
        new_population.append(child)
    return new_population

def run_genetic_algorithm():
    # Run the genetic algorithm for a specified number of generations
    population = generate_initial_population(ANT_POPULATION)
    best_ant = max(population, key=lambda ant: ant.fitness)
    fitness_history = [best_ant.fitness]
    for i in range(GENERATION):
        population = run_generation(population)
        best_ant = max(population, key=lambda ant: ant.fitness)
        fitness_history.append(best_ant.fitness)
    return best_ant, fitness_history
