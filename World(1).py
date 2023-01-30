# Purpose: Creating World that the Agent can interact with
#
#   Info: helicopter world == agent's environment to exploit and learn from
#
#   Developed as part of the Software Agents Course at City University
#
#   Dev: Dan Dixey and Enrico Lopedoto
#
#
import os
import logging

import numpy as np

from Defaults import *

from Wind_Generation import Obstacle_Tracks


class helicopter_world:
    """

    Container for the Grid World

    """

    def __init__(self, file_name=None):
        # Load the Track or Generate on the Fly
        self.file_name = file_name
        self.track = self.load_track(track_name=self.file_name)
        # Get Height and Length of Track
        self.track_height = self.track.shape[0] - 1
        self.track_width = self.track.shape[1]
        # Define the Starting Locations
        self.st_x = 0
        self.st_y = int(self.track_height / 2)
        # Define the Timestamp
        self.ts = 0
        # Define Current Location
        self.loc = (self.st_x, self.st_y)
        # Age of World
        self.trials = 1

    @staticmethod
    def load_track(track_name=None):
        """
        Loading or generating random track

        :param track_name: str
        :return: np.array
        """
        # If no track name is provided generate random using defaults
        if track_name is None:
            logging.warning(
                "Loading Default World - Results are no easily repeatable")
            routes = Obstacle_Tracks(MAX_OBS_HEIGHT=MAX_OBS_HEIGHT,
                                     MAX_OBS_WIDTH=MAX_OBS_WIDTH,
                                     WINDOW_HEIGHT=WINDOW_HEIGHT,
                                     WINDOW_WIDTH=WINDOW_WIDTH,
                                     N_OBSTABLE_GEN=N_OBSTABLE_GEN,
                                     MIN_GAP=MIN_GAP,
                                     N_TRACKS_GEN=N_TRACKS_GEN)
            return routes.generate_tracks[0]
        # Otherwise: Load file from Saved Location
        else:
            logging.warning("Loading Track from Saved Location")
            return np.load(os.path.join(os.getcwd(),
                                        'Model/'
                                        'Track_locations',
                                        track_name))

    def get_location(self, x, y):
        """
        Get Grid World value

        :param x: int
        :param y: int
        :return: int
        """
        return self.track[y][x]

    def check_track_space(self, x, y):
        """
        Check if location is an Obstacle

        :param x: int
        :param y: int
        :return: int
        """
        if (x > self.track_width - 1) or (x < 0) or (y >
                                                     self.track_height - 1) or (y < 0):
            # Where -1 is equivalent to Out of Bounds
            return -1

    def check_goal(self, x, y):
        """
        Checks if the location is at a Goal Location

        :param x: int
        :param y: int
        :return: int
        """
        if x >= self.track_width - 3:
            return 10

    def check_location(self, x, y):
        """
        Wrapper combining many functions into one

        :param x: int
        :param y: int
        :return: int
        """
        # Check if location is within the Bounds
        if self.check_track_space(x=x, y=y) == -1:
            return -1
        # Check if Point is the Goal
        if self.check_goal(x=x, y=y) == 0:
            return 10
        # Otherwise: 1 for Obstacle, 0 for Open Space
        return self.get_location(x=x, y=y)

    def reset(self):
        """
        Reset the Worlds Parameters

        :return: None (resets self objects)
        """
        self.track = self.load_track(track_name=self.file_name)
        # Get Height and Length of Track
        self.track_height = self.track.shape[0] - 1
        self.track_width = self.track.shape[1]
        # Define the Starting Locations
        self.st_x = 0
        self.st_y = int(self.track_height / 2)
        # Define the Timestamp
        self.ts = 0
        # Define Current Location
        self.loc = (self.st_x, self.st_y)

    def update_ts(self):
        """
        Increment World Time by One

        :return: None
        """
        self.ts += 1

    def goal_reached(self, x, y):
        """
        DEV function that would use the Age of the World as an incremental reward

        :param x: int
        :param y: int
        :return: int
        """
        if x >= self.track_width:
            # Reward for reaching the end
            return 100
        else:
            return self.ts
