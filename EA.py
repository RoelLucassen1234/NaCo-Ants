import random
# from Tests import Ant, Tasks
from Environment import Environment
import math
import matplotlib.pyplot as plt  # Import matplotlib for plotting

from Ant import Ant


class EvolutionaryAlgorithm:
    def __init__(self, simulation_length=2000, max_steering=5, exploration_prob=0.3, ph_decay=0.5, detection_range=30,
                 steering_genetic=True, exploration_genetic=True, ph_genetic=True, detection_genetic=True):

        self.simulation_length = simulation_length

        self.max_steering = max_steering
        self.exploration_prob = exploration_prob
        self.ph_decay = ph_decay
        self.detection_range = detection_range

        self.steering_genetic = steering_genetic
        self.exploration_genetic = exploration_genetic
        self.ph_genetic = ph_genetic
        self.detection_genetic = detection_genetic

        self.ANT_POPULATION = 50
        self.GENERATION = 100
        self.MUTATION_RATE = 0.1
        self.EPSILON = 0.1
        self.sim_mode = "EXP"
        random.seed(10)

    # def initial_direction(self) -> float:
    #     # Generate a random angle between 0 and 2*pi
    #     angle = random.uniform(0, 2 * math.pi)
    #     # Adjust the angle to make the movement less jittery
    #     angle += random.randrange(0, 100)
    #     return angle

    def initial_max_steering(self) -> float:
        prob = random.random()
        return prob

    def initial_exploration_prob(self) -> float:
        prob = random.random()
        return prob

    def initial_pheromone_decay(self) -> float:
        prob = random.random()
        return prob

    def initial_detection_range(self) -> float:
        prob = random.random()
        return prob

    def generate_initial_population(self, number_of_ants):
        population = []

        for i in range(number_of_ants):
            steering = self.initial_max_steering()
            explor_prob = self.initial_exploration_prob()
            decay = self.initial_pheromone_decay()
            detect_range = self.initial_detection_range()

            population.append(Ant(max_steering=steering, exploration_prob=explor_prob, ph_decay=decay, detection_range=detect_range))

        return population

    def select_parents(self, population):
        # Select two parents from the population using tournament selection
        parent1 = max(population, key=lambda ant: ant.fitness)
        remaining_population = [ant for ant in population if ant != parent1]
        parent2 = max(remaining_population, key=lambda ant: ant.fitness)
        # parent1 = max(random.sample(population, k=5), key=lambda ant: ant.fitness)
        # parent2 = max(random.sample(population, k=5), key=lambda ant: ant.fitness)
        return parent1, parent2

    def crossover(self, parent1, parent2):
        child = Ant()

        if self.steering_genetic:
            child_steering = parent1.steering * 0.5 + parent2.steering * 0.5
            child.steering = child_steering

        if self.exploration_prob:
            child_exploration = parent1.exploration_prob * 0.5 + parent2.exploration_prob * 0.5
            child.exploration_prob = child_exploration

        if self.ph_genetic:
            child_pheromone = parent1.ph_tick * 0.5 + parent2.ph_tick * 0.5
            child.ph_tick = child_pheromone

        if self.detection_genetic:
            child_detection = parent1.detection_range * 0.5 + parent2.detection_range * 0.5
            child.detection_range = child_detection

        return child

    def mutate(self, ant):
        mutated_ant = Ant()
        if self.steering_genetic:
            if random.random() < self.MUTATION_RATE:
                mutated_ant.steering = ant.steering * random.uniform(0.9, 1.1)
        if self.exploration_genetic:
            if random.random() < self.MUTATION_RATE:
                mutated_ant.exploration_prob = ant.exploration_prob * random.uniform(0.9, 1.1)
        if self.ph_genetic:
            if random.random() < self.MUTATION_RATE:
                mutated_ant.ph_tick = ant.ph_tick * random.uniform(0.9, 1.1)
        if self.detection_genetic:
            if random.random() < self.MUTATION_RATE:
                mutated_ant.detection_range = ant.detection_range * random.uniform(0.9, 1.1)
        return mutated_ant

    def get_fitness_sum(self, population, env):
        # Calculate the sum of the fitness values of all ants in the population
        total_loss = 0
        for ant in population:
            loss = env.calculate_loss(ant, simulation_length=self.simulation_length)
            ant.set_fitness(loss)
            total_loss += loss
        return total_loss

    def highest_fitness(self, population):
        highest = float("-inf")
        ant = None

        for p in population:
            if p.fitness > highest:
                highest = p.fitness
                ant = p

        return ant

    def run_genetic_algorithm(self):
        # Run the genetic algorithm for a specified number of generations
        # TODO 1 Generate initial parameters
        population = self.generate_initial_population(self.ANT_POPULATION)

        env = Environment(self.ANT_POPULATION, sim_mode=self.sim_mode, ants=population)
        fitness_history = []
        self.get_fitness_sum(population, env)
        # best_ant = highest_fitness(population)
        # fitness_history.append(best_ant.fitness)

        # TODO 2 run the model x times
        for i in range(self.GENERATION):
            # TODO 3 calculate loss function
            population = self.run_generation(population)
            f = self.get_fitness_sum(population, env)
            best_ant = self.highest_fitness(population)
            # print('best ant prob: ', best_ant.exploration_prob)
            fitness_history.append(f)
            print(i)

        env.run_simulation(amount_of_runs=self.simulation_length)

        return fitness_history

    def run_generation(self, population):
        new_population = []

        for i in range(len(population)):
            parent1, parent2 = self.select_parents(population)  # TODO 4 pick parents

            child = self.crossover(parent1, parent2)  # TODO 5 breed parents

            # if random.random() < self.MUTATION_RATE:  # TODO 6 mutate children
            child = self.mutate(child)

            new_population.append(child)

        env = Environment(self.ANT_POPULATION, sim_mode=self.sim_mode, ants=new_population)
        env.run_frames(amount_of_runs=self.simulation_length)
        new_population = env.return_ants()
        # get_fitness_sum(new_population, env)
        return new_population


_simulation_length = 2000

_max_steering = 5
_exploration_prob = 0.3
_ph_decay = 0.5
_detection_range = 30

_steering_genetic = True
_exploration_genetic = True
_ph_genetic = True
_detection_genetic = True

ea = EvolutionaryAlgorithm(simulation_length=_simulation_length, max_steering=_max_steering,
                           exploration_prob=_exploration_prob, ph_decay=_ph_decay, detection_range=_detection_range,
                           steering_genetic=_steering_genetic, exploration_genetic=_exploration_genetic,
                           ph_genetic=_ph_genetic, detection_genetic=_detection_genetic)

fitness_history = ea.run_genetic_algorithm()

# Plot the fitness progress
plt.plot(range(len(fitness_history)), fitness_history)
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.title('Fitness Progress')
plt.show()
