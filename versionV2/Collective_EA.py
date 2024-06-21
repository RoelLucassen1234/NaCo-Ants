import random
# from Tests import Ant, Tasks
from versionV2.Environment import Environment
import math
import matplotlib.pyplot as plt  # Import matplotlib for plotting
import numpy as np
from Ant import Ant
from Nest import Nest
from Task import Tasks


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
        self.GENERATION = 20
        self.NUMBER_OF_POPULATIONS = 10
        self.MUTATION_RATE = 0.1
        self.EPSILON = 0.1
        self.sim_mode = "EXP"

        self.nest = Nest([1200 / 3, 800 / 2])

    def initial_max_steering(self) -> float:
        prob = random.uniform(1, 5)
        return prob

    def initial_exploration_prob(self) -> float:
        prob = random.uniform(0.01, 0.4)
        return prob

    def initial_pheromone_decay(self) -> float:
        prob = random.uniform(0.2, 1)
        return prob

    def initial_detection_range(self) -> float:

        prob = random.uniform(1, 120)
        print(prob)
        return prob

    def generate_initial_population(self):

        populations = []

        for i in range(self.NUMBER_OF_POPULATIONS):  # for loop for number of populations
            population = []

            if self.steering_genetic:
                steering = self.initial_max_steering()
            else:
                steering = self.max_steering
            if self.exploration_genetic:
                explor_prob = self.initial_exploration_prob()
            else:
                explor_prob = self.exploration_prob

            if self.ph_genetic:
                decay = self.initial_pheromone_decay()
            else:
                decay = self.ph_decay
            if self.detection_genetic:
                detect_range = self.initial_detection_range()
            else:
                detect_range = self.detection_range

            for j in range(self.ANT_POPULATION):  # for loop for number of ants in one population
                population.append(Ant(max_steering=steering, exploration_prob=explor_prob, ph_decay=decay,
                                      detection_range=detect_range,
                                      position=[self.nest.position[0], self.nest.position[1]]))

            env = Environment(self.ANT_POPULATION, sim_mode=self.sim_mode, ants=population, nest=self.nest)

            populations.append(env)

        return populations

    def select_parents(self, populations):
        # select the two best population from the populations, they will be the parents

        # Helper function to select an individual based on fitness probabilities
        def select_based_on_probability(populations):
            total_fitness = sum(population.fitness for population in populations)
            if total_fitness == 0:
                return np.random.choice(populations)

            probabilities = [population.fitness / total_fitness for population in populations]
            return np.random.choice(populations, p=probabilities)

        # Sort the population by fitness in descending order and select the top 5
        k = 5
        if k > len(populations):
            k = len(populations)
        top_5_populations = sorted(populations, key=lambda population: population.fitness, reverse=True)[:k]
        parent1 = select_based_on_probability(top_5_populations)
        # parent1 = parent1.return_ants()[0]  # Return only one ant

        # Select parent 2: 5 random ants, choose the one with the highest fitness
        sample_2 = random.sample(populations, k=k)
        parent2 = max(sample_2, key=lambda population: population.fitness)
        # parent2 = parent2.return_ants()[0]

        remaining_populations = [population for population in populations if
                                 population != parent1 and population != parent2]

        return parent1, parent2, remaining_populations

    def crossover(self, parent1, parent2):
        parent1 = parent1.return_ants()[0]
        parent2 = parent2.return_ants()[0]

        if self.steering_genetic:
            max_steering1 = parent1.max_steering * 0.9 + parent2.max_steering * 0.1
            max_steering2 = parent1.max_steering * 0.1 + parent2.max_steering * 0.9
        else:
            max_steering1 = self.max_steering
            max_steering2 = self.max_steering

        if self.exploration_genetic:
            exploration_prob1 = parent1.exploration_prob * 0.9 + parent2.exploration_prob * 0.1
            exploration_prob2 = parent1.exploration_prob * 0.1 + parent2.exploration_prob * 0.9
        else:
            exploration_prob1 = self.exploration_prob
            exploration_prob2 = self.exploration_prob

        if self.ph_genetic:
            ph_decay1 = parent1.ph_decay * 0.9 + parent2.ph_decay * 0.1
            ph_decay2 = parent1.ph_decay * 0.1 + parent2.ph_decay * 0.9
        else:
            ph_decay1 = self.ph_decay
            ph_decay2 = self.ph_decay

        if self.detection_genetic:
            detection_range1 = parent1.detection_range * 0.9 + parent2.detection_range * 0.1
            detection_range2 = parent1.detection_range * 0.1 + parent2.detection_range * 0.9
        else:
            detection_range1 = self.detection_range
            detection_range2 = self.detection_range

        # child1 = Ant(max_steering=max_steering1, exploration_prob=exploration_prob1, ph_decay=ph_decay1,
        #              detection_range=detection_range1,
        #              position=[self.nest.position[0], self.nest.position[1]])
        #
        # child2 = Ant(max_steering=max_steering2, exploration_prob=exploration_prob2, ph_decay=ph_decay2,
        #              detection_range=detection_range2,
        #              position=[self.nest.position[0], self.nest.position[1]])
        #
        child1 = [max_steering1, exploration_prob1, ph_decay1, detection_range1]
        child2 = [max_steering2, exploration_prob2, ph_decay2, detection_range2]

        return child1, child2

    def mutate(self, ant):
        new_ant = [0,0,0,0]
        if self.steering_genetic:
            if random.random() < self.MUTATION_RATE:
                new_ant[0] = ant[0] * random.uniform(0.8, 1.2)
            else:
                new_ant[0] = ant[0]
        else:
            new_ant[0] = ant[0]

        if self.exploration_genetic:
            if random.random() < self.MUTATION_RATE:
                new_ant[1] = ant[1] * random.uniform(0.8, 1.2)
            else:
                new_ant[1] = ant[1]
        else:
            new_ant[1] = ant[1]

        if self.ph_genetic:
            if random.random() < self.MUTATION_RATE:
                new_ant[2] = ant[2] * random.uniform(0.8, 1.2)
            else:
                new_ant[2] = ant[2]
        else:
            new_ant[2] = ant[2]

        if self.detection_genetic:
            if random.random() < self.MUTATION_RATE:
                new_ant[3] = ant[3] * random.uniform(0.8, 1.2)
            else:
                new_ant[3] = ant[3]
        else:
            new_ant[3] = ant[3]

        return new_ant

    def make_env_from_ant(self, ant_parameters):
        population = []

        for i in range(self.ANT_POPULATION):
            ant = Ant(max_steering=ant_parameters[0], exploration_prob=ant_parameters[1], ph_decay=ant_parameters[2],
                      detection_range=ant_parameters[3],
                      position=[self.nest.position[0], self.nest.position[1]])
            population.append(ant)

        env = Environment(self.ANT_POPULATION, sim_mode=self.sim_mode, ants=population, nest=self.nest)

        return env

    def get_parameters(self, population):
        ant = population.return_ants()[0]
        max_steering = ant.max_steering
        exploration_prob = ant.exploration_prob
        ph_decay = ant.ph_decay
        detection_range = ant.detection_range
        speed = ant.speed
        return [max_steering, exploration_prob, ph_decay, detection_range, speed]

    def run_genetic_algorithm(self):
        # Run the genetic algorithm for a specified number of generations
        # TODO 1 Generate initial parameters
        populations = self.generate_initial_population()

        fitness_history = []
        parameter_list = []

        for j in range(self.GENERATION):

            print('Generation: ' + str(j))
            if j != 0:
                populations = self.run_generation(populations)
            # print(populations)
            for i in range(self.NUMBER_OF_POPULATIONS):
                population = populations[i]

                # print(self.get_parameters(population))
                # print(len(population.return_ants()))

                food_fitness = population.run_simulation(amount_of_runs=self.simulation_length)
                # food_fitness = population.run_frames(amount_of_runs=self.simulation_length)

                population.set_fitness(food_fitness)



                fitness_history.append(food_fitness)
                parameter = self.get_parameters(population)
                parameter_list.append(parameter)

                print(f"---- {i + 1} ---- food: {food_fitness} ---- parameters: {parameter}")

            # populations = self.run_generation(populations)
            # populations = self.generate_initial_population()
            # print(populations)

        env = sorted(populations, key=lambda p: p.fitness, reverse=True)[0]
        food = env.run_simulation(amount_of_runs=self.simulation_length)
        print(f"--- found food: {food}")

        return fitness_history, parameter_list

    def run_generation(self, populations):
        new_populations = []
        remaining_populations = populations

        for i in range(int(len(populations) / 2)):
            parent1, parent2, remaining_populations = self.select_parents(remaining_populations)  # TODO 4 pick parents

            child1, child2 = self.crossover(parent1, parent2)  # TODO 5 breed parents

            # TODO 6 mutate children
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)

            # Make a new env from the children
            population1 = self.make_env_from_ant(child1)
            population2 = self.make_env_from_ant(child2)

            # List of new populations
            new_populations.append(population1)
            new_populations.append(population2)

        return new_populations


_simulation_length = 100

_max_steering = 5
_exploration_prob = 0.3
_ph_decay = 0.5
_detection_range = 50

_steering_genetic = False
_exploration_genetic = False
_ph_genetic = False
_detection_genetic = True

ea = EvolutionaryAlgorithm(simulation_length=_simulation_length, max_steering=_max_steering,
                           exploration_prob=_exploration_prob, ph_decay=_ph_decay, detection_range=_detection_range,
                           steering_genetic=_steering_genetic, exploration_genetic=_exploration_genetic,
                           ph_genetic=_ph_genetic, detection_genetic=_detection_genetic)

_fitness_history, _parameter_list = ea.run_genetic_algorithm()
print(_fitness_history)
print(_parameter_list)

# Plot the fitness progress
plt.plot(range(len(_fitness_history)), _fitness_history)
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.title('Fitness Progress')
plt.show()
