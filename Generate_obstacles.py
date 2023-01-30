# Purpose: A Class that can be used to generate a number of different entities
#
#   Info: There a three main functions
#
#   1 - Generate Obstacles Metrics - this will generate random features for N obstacles
#                                  - details generated
#                                       - height of obstacle
#                                       - width of obstacle
#                                       - Boolean indicating if the obstacles is located on the top or bottom
#                                       - Starting location within location (X)
#
#   2 - Generate Obstacles - This will create Arrays using the details generated from the previous function
#
#   3 - Generate Tracks - Will collated random Obstacles together
#                           - Trim white space - used to reduce the amount of white space between the obstacles
#
#   Developed as part of the Software Agents Course at City University
#
#   Dev: Dan Dixey and Enrico Lopedoto
#
from random import randint, random, sample

import numpy as np


class Obstacle_Tracks(object):
    """
    Class of Function need to Generate a Simple Track
    """

    def __init__(self, WINDOW_HEIGHT, WINDOW_WIDTH,
                 MAX_OBS_HEIGHT, MAX_OBS_WIDTH, N_OBSTABLE_GEN,
                 MIN_GAP, N_TRACKS_GEN):
        # set design parameters:
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.MAX_OBS_HEIGHT = MAX_OBS_HEIGHT
        self.MAX_OBS_WIDTH = MAX_OBS_WIDTH
        self.N_OBSTABLE_GEN = N_OBSTABLE_GEN
        self.MIN_GAP = MIN_GAP
        self.N_TRACKS_GEN = N_TRACKS_GEN

    def generate_obstacles(self):
        """
        Given the set of input values generate Obstacles

        :return: List(np.array)
        """
        obstacles = self.get_obstable_metrics()
        # Container to store Obstacles
        obstacle_arrays = []

        # Iterate through Obstacle Details
        for nb_obstacle in obstacles:
            empty_array = np.zeros(shape=(self.WINDOW_HEIGHT,
                                          self.WINDOW_WIDTH))
            start_location = 0 if nb_obstacle[2] == 1 else self.WINDOW_HEIGHT
            y, x = start_location - 1, nb_obstacle[3]
            empty_array[y, x] = 1

            for w_value in range(nb_obstacle[0]):
                x_updated = x + w_value

                for h_value in range(nb_obstacle[1]):

                    if nb_obstacle[2] == 1:
                        y_updated = y + h_value
                    else:
                        y_updated = y - h_value
                    # Replace Value

                    empty_array[y_updated, x_updated] = -1

            new_array = self.trim_whitespace(empty_array,
                                             nb_obstacle[2],
                                             self.MIN_GAP)
            obstacle_arrays.append(new_array)

        return obstacle_arrays

    def get_obstable_metrics(self):
        """
        Randomly generates given input constraints Obstacle characteristics

        :return: list(tuple(int, int, int, int))
        """
        obstacle_details = []

        for nb_obstacle in range(self.N_OBSTABLE_GEN):
            # Width Random Size
            width_obs = randint(1, self.MAX_OBS_WIDTH)
            # Height Random Size
            height_obs = randint(1, self.MAX_OBS_HEIGHT)
            # Location Random Selection - 1 if Upper 0 Lower
            location_obs = 1 if random() > 0.5 else 0
            # Start Location
            location_st_obs = randint(0,
                                      self.WINDOW_WIDTH - width_obs)
            obstacle_details.append((width_obs,
                                     height_obs,
                                     location_obs,
                                     location_st_obs))
        return obstacle_details

    def trim_whitespace(self, matrix, details, min_gap):
        """
        Trims unwanted white space from either of the obstacle

        :param matrix: np.array
        :param details: int (obstacle on upper or lower)
        :param min_gap: int
        :return: np.array
        """
        if details == 1:
            row = matrix[0, ]
        else:
            row = matrix[matrix.shape[0] - 1, ]

        min_left = np.argmax(row)
        min_right = np.argmax(row[::-1])

        if min_left > min_gap:
            matrix = matrix[:, min_left - min_gap:]

        if min_right > min_gap:
            matrix = matrix[:, 0:len(row) - (min_right - min_gap)]

        return matrix

    def generate_tracks(self):
        """
        Generate the Track from all the Obstacles

        :return: List(np.array)
        """
        obstacles = self.generate_obstacles()
        tracks = []

        for nb_track in range(self.N_TRACKS_GEN):
            # Get Subset of the Obstacles Lists
            new_obs = sample(obstacles, randint(int(self.N_OBSTABLE_GEN / 4),
                                                self.N_OBSTABLE_GEN))

            track = np.hstack(tuple(new_obs))
            tracks.append(track)

        return tracks
