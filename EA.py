import random
# from Tests import Ant, Tasks
from old_versionV1.Environment import Environment
import math
import matplotlib.pyplot as plt  # Import matplotlib for plotting
import numpy as np
from old_versionV1.Ant import Ant
from Task import Tasks


class EvolutionaryAlgorithm:
    def __init__(self, simulation_length=2000, max_steering=5, exploration_prob=0.3, ph_decay=0.5, detection_range=30,
                 steering_genetic=True, exploration_genetic=True, ph_genetic=True, detection_genetic=True):

        self.simulation_length = simulation_length

        # self.max_steering = max_steering
        # self.exploration_prob = exploration_prob
        # self.ph_decay = ph_decay
        # self.detection_range = detection_range

        self.steering_genetic = steering_genetic
        self.exploration_genetic = exploration_genetic
        self.ph_genetic = ph_genetic
        self.detection_genetic = detection_genetic

        self.ANT_POPULATION = 50
        self.GENERATION = 50
        self.MUTATION_RATE = 0.1
        self.EPSILON = 0.1
        self.sim_mode = "EXP"
        # random.seed(10)

    # def initial_direction(self) -> float:
    #     # Generate a random angle between 0 and 2*pi
    #     angle = random.uniform(0, 2 * math.pi)
    #     # Adjust the angle to make the movement less jittery
    #     angle += random.randrange(0, 100)
    #     return angle

    def initial_max_steering(self) -> float:
        prob = random.uniform(0.01, 0.5)
        return prob

    def initial_exploration_prob(self) -> float:
        prob = random.uniform(0.01, 0.01)
        return prob

    def initial_pheromone_decay(self) -> float:
        prob = random.uniform(1, 3)
        return prob

    def initial_detection_range(self) -> float:
        prob = random.uniform(25, 30)
        return prob

    def generate_initial_population(self, number_of_ants):
        population = []

        for i in range(number_of_ants):
            steering = self.initial_max_steering()
            explor_prob = self.initial_exploration_prob()
            decay = self.initial_pheromone_decay()
            detect_range = self.initial_detection_range()

            population.append(
                Ant(max_steering=steering, exploration_prob=explor_prob, ph_decay=decay, detection_range=detect_range))

        return population

    def select_parents(self, population):
        # Helper function to select an individual based on fitness probabilities
        def select_based_on_probability(ants):
            total_fitness = sum(ant.fitness for ant in ants)
            probabilities = [ant.fitness / total_fitness for ant in ants]
            return np.random.choice(ants, p=probabilities)

        # Sort the population by fitness in descending order and select the top 5
        k = 5
        if k > len(population):
            k = len(population)
        top_5_ants = sorted(population, key=lambda ant: ant.fitness, reverse=True)[:k]
        parent1 = select_based_on_probability(top_5_ants)

        # Select parent 2: 5 random ants, choose the one with the highest fitness
        sample_2 = random.sample(population, k=k)
        parent2 = max(sample_2, key=lambda ant: ant.fitness)

        remaining_population = [ant for ant in population if ant != parent1 and ant != parent2]

        return parent1, parent2, remaining_population

    def crossover(self, parent1, parent2):
        child1 = Ant()
        child2 = Ant()

        if self.steering_genetic:
            child1.max_steering = parent1.max_steering * 0.6 + parent2.max_steering * 0.4
            child2.max_steering = parent1.max_steering * 0.4 + parent2.max_steering * 0.6

        if self.exploration_genetic:
            child1.exploration_prob = parent1.exploration_prob * 0.6 + parent2.exploration_prob * 0.4
            child2.exploration_prob = parent1.exploration_prob * 0.4 + parent2.exploration_prob * 0.6

        if self.ph_genetic:
            child1.ph_tick = parent1.ph_tick * 0.6 + parent2.ph_tick * 0.4
            child2.ph_tick = parent1.ph_tick * 0.4 + parent2.ph_tick * 0.6

        if self.detection_genetic:
            child1.detection_range = parent1.detection_range * 0.6 + parent2.detection_range * 0.4
            child2.detection_range = parent1.detection_range * 0.4 + parent2.detection_range * 0.6

        return child1, child2

    def mutate(self, ant):
        mutated_ant = Ant()
        if self.steering_genetic:
            if random.random() < self.MUTATION_RATE:
                ant.max_steering = ant.max_steering * random.uniform(0.9, 1.1)
        if self.exploration_genetic:
            if random.random() < self.MUTATION_RATE:
                ant.exploration_prob = ant.exploration_prob * random.uniform(0.9, 1.1)
        if self.ph_genetic:
            if random.random() < self.MUTATION_RATE:
                ant.ph_tick = ant.ph_tick * random.uniform(0.9, 1.1)
        if self.detection_genetic:
            if random.random() < self.MUTATION_RATE:
                ant.detection_range = ant.detection_range * random.uniform(0.9, 1.1)
        return ant

    def calculate_loss(self, ant, env, simulation_length=2000):
        def calculate_distance(point1, point2):
            # print(point1, point2)
            x1, y1 = point1
            x2, y2 = point2

            delta_x = x2 - x1
            delta_y = y2 - y1

            distance = math.sqrt(delta_x ** 2 + delta_y ** 2)
            # print(distance)

            return distance

        max_distance = calculate_distance([0,0], [env.width, env.height])
        distance_from_home = calculate_distance(ant.position, env.nest.position)

        # Did the ant find the nest
        if ant.current_task == Tasks.GatherAnts:  # Ant found home

            steps_to_home = ant.steps_to_home
            loss = ((simulation_length - steps_to_home) / simulation_length)  + 0.5

        else:  # Ant not found home
            loss = ((max_distance - distance_from_home) / max_distance) / 2

        # loss = ants_found_food + (ants_at_food / len(self.ants))
        # loss = ants_found_home + ((amount_of_runs - steps_to_home) / amount_of_runs)
        # loss = ant_found_home + (amount_of_runs - steps_to_home)
        loss += 0.0001
        # print(loss)
        return loss

    def get_fitness_sum(self, population, env):
        # Calculate the sum of the fitness values of all ants in the population
        total_loss = 0
        for ant in population:
            loss = self.calculate_loss(ant, env, simulation_length=self.simulation_length)
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
            self.top_5_highest_fitness_ants(population)
            fitness_history.append(f)
            print(i)

        env.run_frames(amount_of_runs=self.simulation_length)

        return fitness_history

    def top_5_highest_fitness_ants(self, population):

        sorted_ants = sorted(population, key=lambda ant: ant.fitness, reverse=True)
        top_5_ants = sorted_ants[:5]
        i = 1
        for best_ant in top_5_ants:
            print(
                f'Best Ant {i}: expl_prob: {best_ant.exploration_prob}, detection_range = {best_ant.detection_range}, steering: {best_ant.max_steering}. fitness: {best_ant.fitness}  ', )
            i += 1

    def run_generation(self, population):
        new_population = []
        remaining_population = population
        for i in range(int(len(population) / 2)):
            parent1, parent2, remaining_population = self.select_parents(remaining_population)  # TODO 4 pick parents

            child1, child2 = self.crossover(parent1, parent2)  # TODO 5 breed parents

            # if random.random() < self.MUTATION_RATE:  # TODO 6 mutate children
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)

            new_population.append(child1)
            new_population.append(child2)

        print(f"new Popilation Amount {len(new_population)}")
        env = Environment(self.ANT_POPULATION, sim_mode=self.sim_mode, ants=new_population)
        env.run_frames(amount_of_runs=self.simulation_length)
        new_population = env.return_ants()
        # get_fitness_sum(new_population, env)
        return new_population


_simulation_length = 2000

_max_steering = 5
_exploration_prob = 0.01
_ph_decay = 0.5
_detection_range = 30

_steering_genetic = True
_exploration_genetic = False
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
