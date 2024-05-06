import numpy as np
import random
import Tests

import math


def round_up_to_even(f):
    return math.ceil(f / 2.) * 2


def EA():
    epsilon = 0.1
    number_of_models = 10

    # TODO 1 generate x number of random parameters
    direction = random.sample(range(0, 360), number_of_models)
    velocity = random.sample(range(0, 20), number_of_models)

    # TODO 2 run the ant model x times
    metrics_dict = {}

    for i in range(number_of_models):

        ant = Tests.Ant()
        distance, lost_ants = ant.enviroment(direction[i], velocity[i])

        # TODO 3 calculate x loss functions
        metric = loss_function(distance, lost_ants)
        metrics_dict[metric] = direction[i], velocity[i]

    # TODO 4 using the e-greedy policy, pick N models
    # Even number of parents
    N = round_up_to_even(number_of_models / 2)

    metrics = list(metrics_dict.keys())
    chosen_metrics = []

    for n in range(N):
        p = random.random()
        if p < epsilon:
            ch = random.choice(metrics)
        else:
            ch = max(metrics)

        metrics.remove(ch)
        chosen_metrics.append(ch)

    # TODO 5 breed these N models
    N2 = int(N/2)
    direction_children = []
    velocity_children = []
    for n in range(N2):
        parent1 = metrics_dict[chosen_metrics[n]]
        parent2 = metrics_dict[chosen_metrics[n+N2]]

        # direction
        dir1 = parent1[0]
        dir2 = parent2[0]

        dir_child = (dir1 + dir2) / 2

        dir_child += random

        direction_children.append(dir_child)

        # velocity
        vel1 = parent1[1]
        vel2 = parent2[1]

        vel_child = (vel1 + vel2) / 2
        velocity_children.append(vel_child)

    # TODO 6 mutate the children
    #
    # direction = dir_child + random.random()
    # vel

    # TODO 7 repeat step 2-6


def loss_function(distance, lost_ants):
    # distance the ants walked to reach the nest
    # the number of ants that did not reach the nest

    return distance + lost_ants
