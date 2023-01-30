# Purpose: Test Script to Ensure that as the complexity of the Scripts Grows functionality can be checked
#
#   Info: Uses py.test to test each of the track building functions are working
#
#   Running the Test from the COMMAND LINE: py.test test.py
#
#   Developed as part of the Software Agents Course at City University
#
#   Dev: Dan Dixey and Enrico Lopedoto
#
#
import os
import logging

import numpy as np

from Model.Wind_Generation import Obstacle_Tracks
from Model.Defaults import *
from Model.World import helicopter_world

# Logging Controls Level of Printing
logging.basicConfig(format='[%(asctime)s] : [%(levelname)s] : [%(message)s]',
                    level=logging.INFO)


def test_creating_obstacles_details():
    routes = Obstacle_Tracks(MAX_OBS_HEIGHT=MAX_OBS_HEIGHT,
                             MAX_OBS_WIDTH=MAX_OBS_WIDTH,
                             WINDOW_HEIGHT=WINDOW_HEIGHT,
                             WINDOW_WIDTH=WINDOW_WIDTH,
                             N_OBSTABLE_GEN=N_OBSTABLE_GEN,
                             MIN_GAP=MIN_GAP,
                             N_TRACKS_GEN=N_TRACKS_GEN)
    # Get Obstacles Irregularities
    output1 = routes.get_obstable_metrics
    assert isinstance(output1, list) and isinstance(
        output1[0], tuple), 'Types Not as Expected in Output1'


def test_creating_obstacles():
    routes = Obstacle_Tracks(MAX_OBS_HEIGHT=MAX_OBS_HEIGHT,
                             MAX_OBS_WIDTH=MAX_OBS_WIDTH,
                             WINDOW_HEIGHT=WINDOW_HEIGHT,
                             WINDOW_WIDTH=WINDOW_WIDTH,
                             N_OBSTABLE_GEN=N_OBSTABLE_GEN,
                             MIN_GAP=MIN_GAP,
                             N_TRACKS_GEN=N_TRACKS_GEN)
    # Generate Obstacles
    output2 = routes.generate_obstacles
    assert isinstance(output2, list) and isinstance(
        output2[0], np.ndarray), 'Types Not as Expected in Output2'


def test_creating_tracks():
    routes = Obstacle_Tracks(MAX_OBS_HEIGHT=MAX_OBS_HEIGHT,
                             MAX_OBS_WIDTH=MAX_OBS_WIDTH,
                             WINDOW_HEIGHT=WINDOW_HEIGHT,
                             WINDOW_WIDTH=WINDOW_WIDTH,
                             N_OBSTABLE_GEN=N_OBSTABLE_GEN,
                             MIN_GAP=MIN_GAP,
                             N_TRACKS_GEN=N_TRACKS_GEN)
    # Generate Tracks / Paths
    output3 = routes.generate_tracks
    assert isinstance(output3, list) and isinstance(
        output3[0], np.ndarray) and len(output3) == N_TRACKS_GEN, \
        'Types Not as Expected in Output3'


def test_saving_obstacles():
    routes = Obstacle_Tracks(MAX_OBS_HEIGHT=MAX_OBS_HEIGHT,
                             MAX_OBS_WIDTH=MAX_OBS_WIDTH,
                             WINDOW_HEIGHT=WINDOW_HEIGHT,
                             WINDOW_WIDTH=WINDOW_WIDTH,
                             N_OBSTABLE_GEN=N_OBSTABLE_GEN,
                             MIN_GAP=MIN_GAP,
                             N_TRACKS_GEN=N_TRACKS_GEN)
    # Generate Obstacles
    output4 = routes.generate_obstacles
    # Get the first obstacle
    saved = output4[0]
    # Save the obstacle
    np.save(os.path.join(os.getcwd(),
                         'Tests',
                         'Test_Obstacle'), saved)
    # Load obstacle
    loaded = np.load(os.path.join(os.getcwd(),
                                  'Tests',
                                  'Test_Obstacle.npy'))
    assert saved.shape == loaded.shape, 'Dimensions Incorrect'


def test_saving_tracks():
    routes = Obstacle_Tracks(MAX_OBS_HEIGHT=MAX_OBS_HEIGHT,
                             MAX_OBS_WIDTH=MAX_OBS_WIDTH,
                             WINDOW_HEIGHT=WINDOW_HEIGHT,
                             WINDOW_WIDTH=WINDOW_WIDTH,
                             N_OBSTABLE_GEN=N_OBSTABLE_GEN,
                             MIN_GAP=MIN_GAP,
                             N_TRACKS_GEN=N_TRACKS_GEN)
    # Generate Obstacles
    output5 = routes.generate_tracks
    # Get the first obstacle
    saved = output5[0]
    # Save the obstacle
    np.save(os.path.join(os.getcwd(),
                         'Tests',
                         'Test_Track'), saved)
    # Load obstacle
    loaded = np.load(os.path.join(os.getcwd(),
                                  'Tests',
                                  'Test_Track.npy'))
    assert saved.shape == loaded.shape, 'Dimensions Incorrect'


def test_world_load_defaults():
    world = helicopter_world()
    assert isinstance(world.track, np.ndarray), 'Loading Default Failed'


def test_world_loading():
    world = helicopter_world(file_name=os.path.join(os.getcwd(),
                                                    "Tests",
                                                    "Test_Track.npy"))
    loaded_track = np.load(os.path.join(os.getcwd(),
                                        "Tests",
                                        "Test_Track.npy"))
    assert loaded_track.shape == world.track.shape, \
        "Loading Track into World Failed"
