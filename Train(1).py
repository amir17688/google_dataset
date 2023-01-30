# Purpose: Main Function - Training Models
#
#   Info: Change the Parameters at the top of the scrip to change how the Agent interacts
#
#   Developed as part of the Software Agents Course at City University
#
#   Dev: Dan Dixey and Enrico Lopedoto
#
#   Updated: 10/3/2016
#
import logging
from random import choice
from time import sleep
from time import time

import matplotlib
import matplotlib.pyplot as plt

from Model import World as W
from Model.Helicopter import helicopter
from Model.Plotting import plotting_model
from Settings import *

matplotlib.style.use('ggplot')


# Logging Controls Level of Printing
logging.basicConfig(format='[%(asctime)s] : [%(levelname)s] : [%(message)s]',
                    level=logging.INFO)


# Model Settings
case = 'case_five'
settings_ = case_lookup[case]
iterations, settings = get_indicies(settings_)

# Plot Settings
plot_settings = dict(print_up_to=-1,
                     end_range=list(range(settings['trials'] - 10,
                                          settings['trials'] + 1)),
                     print_rate=5)

HeliWorld = W.helicopter_world(file_name="Track_1.npy")
# file_name=None - Loads a Randomly Generated Track
Helicopter1 = helicopter(world=HeliWorld,
                         settings=settings)

st = time()
time_metrics = []
a = np.zeros(shape=(HeliWorld.track_height,
                    HeliWorld.track_width))


logging.info('Dealing with Case: {}'.format(case))
for value_iter in range(iterations):

    if value_iter > 0:
        settings = get_settings(dictionary=settings_,
                                ind=value_iter)
        HeliWorld = W.helicopter_world(file_name="Track_1.npy")
        Helicopter1 = helicopter(world=HeliWorld,
                                 settings=settings)
        a = np.zeros(shape=(HeliWorld.track_height,
                            HeliWorld.track_width))
        t_array = []  # Storing Time to Complete
        f_array = []  # Storing Final Locations
        b_array = []  # Storing Full Control
        logging.info('Changing Values: {}'.format(settings_['change_values']))

    continue_on, name = check_files(settings, case, value_iter)
    logging.info('Dealing with Iteration: {}'.format(value_iter))

    if not continue_on:
        while HeliWorld.trials <= settings['trials']:

            # On the Last Trail give the Model full control
            if HeliWorld.trials == settings[
                    'trials'] or HeliWorld.trials in plot_settings['end_range']:
                Helicopter1.ai.epsilon, settings['epsilon'] = 0, 0

            # Print out logging metrics
            if HeliWorld.trials % plot_settings[
                    'print_rate'] == 0 and HeliWorld.trials > 0:
                rate = ((time() - st + 0.01) / HeliWorld.trials)
                value = [HeliWorld.trials, rate]
                time_metrics.append(value)
                logging.info(
                    "Trials Completed: {} at {:.4f} seconds / trial".format(value[0], value[1]))

            # Inner loop of episodes
            while True:
                output = Helicopter1.update()

                if HeliWorld.trials == settings['trials']:
                    b_array.append(Helicopter1.current_location)

                if not output:
                    try:
                        f_array.append(
                            [HeliWorld.trials, Helicopter1.current_location[0]])
                    except Exception as e:
                        f_array.append(
                            [HeliWorld.trials, 0])
                        pass

                    Helicopter1.reset()
                    rate = (time() - st + 0.01) / HeliWorld.trials
                    value = [HeliWorld.trials,
                             rate]
                    t_array.append(value)
                    if HeliWorld.trials <= plot_settings[
                            'print_up_to'] or HeliWorld.trials in plot_settings['end_range']:
                        results['paths'].append(path)
                        path = []

                    if Helicopter1.current_location[
                            0] >= HeliWorld.track_width - 2:
                        logging.info('Completed')

                    break

                if HeliWorld.trials <= plot_settings[
                        'print_up_to'] or HeliWorld.trials in plot_settings['end_range']:
                    # Primary Title
                    rate = (time() - st + 0.01) / HeliWorld.trials
                    value = [HeliWorld.trials,
                             rate]
                    path.append(Helicopter1.current_location)

                try:
                    pos, array_masked = Helicopter1.return_q_view()
                    a[:, pos - 1] += array_masked
                except Exception as e:
                    pass

            logging.debug('Starting next iteration')
            HeliWorld.trials += 1

        Helicopter1.ai.save_model(name=name)

        et = time()
        logging.info(
            "Time Taken: {} seconds for Iteration {}".format(
                et - st, value_iter + 1))

        if settings['model'] < 3:
            logging.info("Plotting the Q-Matrix")
            model_plot = plotting_model()
            model_plot.get_q_matrix(model_q=Helicopter1.ai.q,
                                    nb_actions=settings['nb_actions'])
            model_plot.plot_q_matrix('Q-Matrix - {}'.format(name))
            q_data = model_plot.get_details()
            results['q_matrix'].append(q_data)

        if value_iter > 0:
            results = load_results(
                os.path.join(
                    os.getcwd(),
                    'Results',
                    case),
                settings['model'])

        # Record Results
        results['time_chart'].append(t_array),
        results['final_location'].append(f_array)
        results['best_test'].append(b_array)
        results['q_plot'].append(a.tolist())
        results['model_names'].append(settings)
        save_results(case, settings, results)
    else:
        logging.info('Results Already exist... Skipping')


plot = False
if settings_['model'] < 3 and plot:
    fig = plt.figure()
    plt.title('Real-time Plot of Helicopter Path', fontsize=10)
    plt.xlabel('Track Length', fontsize=8)
    plt.ylabel('Track Width', fontsize=8)
    my_axis = plt.gca()
    my_axis.set_xlim(0, HeliWorld.track_width)
    my_axis.set_ylim(0, HeliWorld.track_height)
    im1 = plt.imshow(HeliWorld.track,
                     cmap=plt.cm.jet,
                     interpolation='nearest',
                     vmin=-1,
                     vmax=8)
    plt.colorbar(im1, fraction=0.01, pad=0.01)
    # Plotting Colors
    colors = ['black', 'green', 'red', 'cyan', 'magenta',
              'yellow', 'blue', 'white', 'fuchsia', 'orangered', 'steelblue']

    for val, data in enumerate(results['paths']):
        x, y = [], []

        for step in data:
            x.append(step[0])
            y.append(step[1])

        plt.scatter(x,
                    y,
                    s=np.pi * (1 * (1.5))**2,
                    c=choice(colors))
        plt.pause(0.5)
        sleep(0.5)

    fig1 = plt.figure()
    plt.title('Q Plot of Helicopter Path', fontsize=10)
    plt.xlabel('Track Length', fontsize=8)
    plt.ylabel('Track Width', fontsize=8)
    my_axis = plt.gca()
    my_axis.set_xlim(0, HeliWorld.track_width)
    my_axis.set_ylim(0, HeliWorld.track_height)
    im1 = plt.imshow(a,
                     cmap=plt.cm.jet,
                     interpolation='nearest')
    plt.colorbar(im1, fraction=0.01, pad=0.01)
