import random
# from Tests import Ant, Tasks
from Environment import Environment
import math
import matplotlib.pyplot as plt  # Import matplotlib for plotting

from Ant import Ant

ANT_POPULATION = 50
GENERATION = 100
MUTATION_RATE = 0.1
EPSILON = 0.1
sim_mode = "EXP"
random.seed(10)


class EvolutionaryAlgorithm:
    def __init__(self, max_steering=5, exploration_prob=0.3, ph_decay=0.5, detection_range=30, simulation_length=2000,
                 steering_genetic=True, exploration_genetic=True, ph_genetic=True, detection_genetic=True):
        self.max_steering = max_steering
        self.exploration_prob = exploration_prob
        self.ph_decay = ph_decay
        self.detection_range = detection_range
        self.simulation_length = simulation_length
        self.steering_genetic = steering_genetic
        self.exploration_genetic = exploration_genetic
        self.ph_genetic = ph_genetic
        self.detection_genetic = detection_genetic

    def initial_direction(self) -> float:
        # Generate a random angle between 0 and 2*pi
        angle = random.uniform(0, 2 * math.pi)
        # Adjust the angle to make the movement less jittery
        angle += random.randrange(0, 100)
        return angle

    def initial_exploration_prob(self) -> float:
        prob = random.random()
        return prob

    def generate_initial_population(self, number_of_ants):
        population = []
        init_exploration_prob = []

        for i in range(number_of_ants):
            explor_prob = self.initial_exploration_prob()
            init_exploration_prob.append(explor_prob)
            population.append(Ant(exploration_prob=explor_prob))

        return population, init_exploration_prob

    import random

    def select_parents(self, population):
        # Select two parents from the population using tournament selection
        parent1 = max(population, key=lambda ant: ant.fitness)
        remaining_population = [ant for ant in population if ant != parent1]
        parent2 = max(remaining_population, key=lambda ant: ant.fitness)
        # parent1 = max(random.sample(population, k=5), key=lambda ant: ant.fitness)
        # parent2 = max(random.sample(population, k=5), key=lambda ant: ant.fitness)
        return parent1, parent2

    def crossover(self, parent1, parent2, exploration, steering, pheromone, speed):
        # # Perform crossover for wandering_strength
        # child_wandering_strength = parent1.wandering_strength * 0.5 + parent2.wandering_strength * 0.5
        #
        # # Perform crossover for steering

        child = Ant()

        if exploration:
            child_exploration = parent1.exploration_prob * 0.5 + parent2.exploration_prob * 0.5
            # child = Boid(exploration_prob=child_exploration)
            child.exploration_prob = child_exploration

        if steering:
            child_steering = parent1.steering * 0.5 + parent2.steering * 0.5
            # child = Boid(st=child_steering)
            child.steering = child_steering

        if pheromone:
            child_pheromone = parent1.pheromone * 0.5 + parent2.pheromone * 0.5
            # child = Boid(pheromone=child_pheromone)
            child.ph_tick = child_pheromone

        if speed:
            child_speed = parent1.speed * 0.5 + parent2.speed * 0.5
            # child = Boid(speed=child_speed)
            child.speed = child_speed

        return child

    def mutate(self, ant, exploration, steering, pheromone, speed):
        # Perform mutation on an ant's path
        # mutated_ant = Boid(exploration_prob=ant.exploration_prob * random.uniform(0.9, 1.1))
        mutated_ant = Ant()
        if exploration:
            mutated_ant.exploration_prob = ant.exploration_prob * random.uniform(0.9, 1.1)
        if steering:
            mutated_ant.steering = ant.steering * random.uniform(0.9, 1.1)
        if pheromone:
            mutated_ant.ph_tick = ant.ph_tick * random.uniform(0.9, 1.1)
        if speed:
            mutated_ant.speed = ant.speed * random.uniform(0.9, 1.1)
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

    def run_genetic_algorithm(self, exploration, steering, pheromone, speed):
        # Run the genetic algorithm for a specified number of generations
        # TODO 1 Generate initial parameters
        population, _ = self.generate_initial_population(ANT_POPULATION)

        env = Environment(ANT_POPULATION, sim_mode=sim_mode, ants=population)
        fitness_history = []
        self.get_fitness_sum(population, env)
        # best_ant = highest_fitness(population)
        # fitness_history.append(best_ant.fitness)

        # TODO 2 run the model x times
        for i in range(GENERATION):
            # TODO 3 calculate loss function
            population = self.run_generation(population, exploration=exploration, steering=steering,
                                             pheromone=pheromone, speed=speed)
            f = self.get_fitness_sum(population, env, exploration=exploration, steering=steering, pheromone=pheromone,
                                     speed=speed)
            best_ant = self.highest_fitness(population)
            # print('best ant prob: ', best_ant.exploration_prob)
            fitness_history.append(f)
            print(i)

        env.run_simulation(amount_of_runs=self.simulation_length)

        return fitness_history

    def run_generation(self, population, exploration, steering, pheromone, speed):
        new_population = []

        for i in range(len(population)):

            parent1, parent2 = self.select_parents(population)  # TODO 4 pick parents

            child = self.crossover(parent1, parent2, exploration=exploration, steering=steering, pheromone=pheromone,
                                   speed=speed)  # TODO 5 breed parents

            if random.random() < MUTATION_RATE:  # TODO 6 mutate children
                child = self.mutate(child, exploration=exploration, steering=steering, pheromone=pheromone, speed=speed)
            new_population.append(child)

        env = Environment(ANT_POPULATION, sim_mode=sim_mode, ants=new_population)
        env.run_frames(amount_of_runs=self.simulation_length)
        new_population = env.return_ants()
        # get_fitness_sum(new_population, env)
        return new_population


max_steering = 5
exploration_prob = 0.3
ph_decay = 0.5
detection_range = 30
simulation_length = 2000

steering_genetic = True
exploration_genetic = True
ph_genetic = True
detection_genetic = True

ea = EvolutionaryAlgorithm(max_steering=max_steering, exploration_prob=exploration_prob, ph_decay=ph_decay,
                           detection_range=detection_range, simulation_length=simulation_length,
                           steering_genetic=steering_genetic, exploration_genetic=exploration_genetic, ph_genetic=ph_genetic, detection_genetic=detection_genetic)

fitness_history = ea.run_genetic_algorithm(amount_of_runs=2000, exploration=True, steering=True, pheromone=True,
                                        speed=True)

# Plot the fitness progress
plt.plot(range(len(fitness_history)), fitness_history)
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.title('Fitness Progress')
plt.show()
