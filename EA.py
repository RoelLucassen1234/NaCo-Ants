import random
from Tests import Ant, Tasks
from Environment import Environment
import math
import math
import matplotlib.pyplot as plt  # Import matplotlib for plotting

ANT_POPULATION = 50
GENERATION = 20
MUTATION_RATE = 0.1
EPSILON = 0.1
sim_mode = "EXP"


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
        population.append(Ant(direction=15))

    return population, init_direction


def select_parents(population):
    # Select two parents from the population using tournament selection
    parent1 = max(random.sample(population, k=5), key=lambda ant: ant.fitness)
    parent2 = max(random.sample(population, k=5), key=lambda ant: ant.fitness)
    return parent1, parent2


def crossover(parent1, parent2):
    # Perform crossover for wandering_strength
    child_wandering_strength = parent1.wandering_strength * 0.5 + parent2.wandering_strength * 0.5

    # Perform crossover for steering
    child_steering = parent1.steering * 0.5 + parent2.steering * 0.5

    # Create the child with the crossover values
    child = Ant(wandering_strength=child_wandering_strength, steering=child_steering)
    return child


def mutate(ant):
    # Perform mutation on an ant's path
    mutated_ant = Ant(wandering_strength=ant.wandering_strength * random.uniform(0.9, 1.1),
                      steering=ant.steering * random.uniform(0.9, 1.1))
    return mutated_ant


def get_fitness_sum(population, env):
    # Calculate the sum of the fitness values of all ants in the population
    for ant in population:
        fitness = env.calculate_loss(ant)
        ant.fitness = fitness


def highest_fitness(population):
    highest = float("-inf")
    ant = None

    for p in population:
        if p.fitness > highest:
            highest = p.fitness
            ant = p

    return ant


def run_genetic_algorithm():
    # Run the genetic algorithm for a specified number of generations
    population, _ = generate_initial_population(ANT_POPULATION)

    env = Environment(50, sim_mode=sim_mode, ants=population)
    fitness_history = []
    get_fitness_sum(population, env)
    best_ant = highest_fitness(population)
    fitness_history.append(best_ant.fitness)

    for i in range(GENERATION):
        population = run_generation(population, env)
        get_fitness_sum(population,env)
        best_ant = highest_fitness(population)
        fitness_history.append(best_ant.fitness)
        print(i)

    return best_ant, fitness_history


def run_generation(population, env):
    new_population = []
    for i in range(len(population)):
        parent1, parent2 = select_parents(population)
        child = crossover(parent1, parent2)
        if random.random() < MUTATION_RATE:
            child = mutate(child)
        new_population.append(child)
    env = Environment(50, sim_mode=sim_mode, ants=new_population)
    env.run_frames()
    new_population = env.return_ants()
    get_fitness_sum(new_population, env)
    return new_population


best_ant, fitness_history = run_genetic_algorithm()

# Plot the fitness progress
plt.plot(range(len(fitness_history)), fitness_history)
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.title('Fitness Progress')
plt.show()
