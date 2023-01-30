# Purpose: Script containing Settings for the Model
#
#   Info: Change the Parameters at the top of the scrip to change how the Agent interacts
#
#   Developed as part of the Software Agents Course at City University
#
#   Dev: Dan Dixey and Enrico Lopedoto
#
#   Updated: 10/3/2016
#
import json
import os

import numpy as np

model_version = 2

# Case 1 - Default Evaluation
# Complete: 1, 2
case_one = dict(trials=500,
                completed=100,
                crashed=-100,
                open=1,
                alpha=0.75,
                epsilon=0.15,
                gamma=0.99,
                nb_actions=5,
                model=model_version,
                epsilon_decay=0.9,
                epsilon_action=6000,
                change_values=[],
                train=True)

# Case 2 - Change Gamma values
# Complete: 1, 2, 3
case_two = dict(trials=500,
                completed=100,
                crashed=-100,
                open=1,
                alpha=0.75,
                epsilon=0.15,
                gamma=np.arange(0.1, 1.1, 0.1),
                nb_actions=5,
                model=model_version,
                epsilon_decay=0.9,
                epsilon_action=6000,
                change_values=['gamma'],
                train=True)

# Case 3 - Change Learning Rates
# Complete: 1, 2
# Important to Note: DQN implementation does not use Alpha
case_three = dict(trials=200,
                  completed=500,
                  crashed=-100,
                  open=5,
                  alpha=np.arange(0.1, 1.1, 0.1),
                  epsilon=0.75,
                  gamma=0.7,
                  nb_actions=5,
                  model=model_version,
                  epsilon_decay=0.9,
                  epsilon_action=6000,
                  change_values=['alpha'],
                  train=True)

# Case 4 - Different policies (epsilon)
# Complete: 1, 2, 3
case_four = dict(trials=550,
                 completed=100,
                 crashed=-100,
                 open=1,
                 alpha=0.65,
                 epsilon=np.arange(0.1, 1.1, 0.1),
                 gamma=0.7,
                 nb_actions=5,
                 model=model_version,
                 epsilon_decay=0.9,
                 epsilon_action=6000,
                 change_values=['epsilon'],
                 train=True)

# Case 5 - different Reward functions
# Complete: 1, 2
case_five = dict(trials=550,
                 completed=np.arange(50, 235, 20),
                 crashed=np.arange(-50, -235, -20),
                 open=np.arange(-5, 5),
                 alpha=0.75,
                 epsilon=0.15,
                 gamma=0.7,
                 nb_actions=5,
                 model=model_version,
                 epsilon_decay=0.9,
                 epsilon_action=6000,
                 change_values=['completed',
                                'crashed',
                                'open'],
                 train=True)

# Case Dictionary
case_lookup = dict(case_one=case_one,
                   case_two=case_two,
                   case_three=case_three,
                   case_four=case_four,
                   case_five=case_five)


def save_results(case, settings, results):
    """
    Save all results to a JSON file

    :param case: str
    :param settings: dict
    :param results: list
    :return: None
    """
    f = open(
        os.path.join(
            os.getcwd(),
            'Results',
            case,
            'Model{}'.format(
                settings['model']) +
            '.json'),
        'w').write(
        json.dumps(results))


def load_results(directory, model):
    """
    Loading the Settings File

    :param directory: str
    :param model: int
    :return: dict
    """
    return json.loads(
        open(directory + '/Model{}.json'.format(model), 'r').read())


def check_files(settings, case, value_iter):
    """
    In case the Train File Stops...

    :param settings: dict
    :param case: str
    :param value_iter: int
    :return: Boolean
    """
    name = 'model_{}_case_{}_iter_{}'.format(
        settings['model'],
        case.split('_')[1],
        value_iter)
    path = os.path.join(os.getcwd(), 'Results', case) + \
        '/Model{}'.format(settings['model']) + '.json'
    results_file = os.path.isfile(path)
    # Depending on Model No. Check if Model Memory is Saved
    if settings['model'] < 3:
        path = os.path.join(
            os.getcwd(), 'Model/NN_Model/', name + '.pkl')
        model_saved = os.path.isfile(path)
    else:
        path = os.path.join(
            os.getcwd(),
            'Model/NN_Model/',
            name + '_weights.h5')
        model_saved = os.path.isfile(path)

    if results_file and model_saved:
        continue_on = True
    else:
        continue_on = False

    return continue_on, name


def get_indicies(data, ind=0):
    """
    Get the number of Iterations Required for Dictionary

    :param data: dict
    :param ind: int
    :return: tuple(int, dict)
    """
    if len(data['change_values']) > 0:
        return 10, get_settings(data)
    else:
        return 1, data


# Get New Dictionary values
def get_settings(dictionary=None, ind=0):
    """
    Get Next value in dictionary

    :param dictionary: dict
    :param ind: int
    :return: dict
    """
    new_dict = dictionary.copy()
    for each_value in dictionary['change_values']:
        new_dict[each_value] = dictionary[each_value][ind]
    return new_dict

results = dict(time_chart=[],
               final_location=[],
               best_test=[],
               q_plot=[],
               model_names=[],
               q_matrix=[],
               paths=[])

t_array = []  # Storing Time to Complete
f_array = []  # Storing Final Locations
b_array = []  # Storing Full Control
path = []
