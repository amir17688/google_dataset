# Purpose: Agent uses the Q-Learning Algorithm to Interact with the Environment
#
#   Info: Class that Implements the Q-Learning Algorithm
#
#   Developed as part of the Software Agents Course at City University
#
#   Dev: Dan Dixey and Enrico Lopedoto
#
#
import logging
import os
import pickle
from random import choice, random

import numpy as np

try:
    from keras.layers.convolutional import Convolution1D, MaxPooling1D
    from keras.layers.core import Dense, Dropout, Activation, Flatten
    from keras.layers.embeddings import Embedding
    from keras.layers.recurrent import LSTM
    from keras.models import Sequential
    from keras.optimizers import RMSprop, Adadelta
except:
    logging.warning(
        'Unable to Import Deep Learning Modules - Are they installed?')
    pass


class Q_Learning_Algorithm:
    """
    Basic Implementation of the Q-Learning Algorithm
    """

    def __init__(self, settings=None):
        """
        :param settings: dictionary of settings
        """
        assert settings is not None, 'Pass the Settings'
        self.q = {}
        self.directory = os.path.join(os.getcwd(), 'Model/NN_Model/')
        self.actions = range(settings['nb_actions'])
        self.alpha = settings['alpha']
        self.epsilon = settings['epsilon']
        self.gamma = settings['gamma']
        self.train = settings['train']

    def get_Qvalue(self, state, action):
        return self.q.get((state, action), 0.0)

    def learnQ(self, state, action, reward, value):
        old_value = self.q.get((state, action), None)

        if old_value is None:
            self.q[(state, action)] = reward
        else:
            self.q[(state, action)] = old_value + \
                self.alpha * (value - old_value)

    def choose_Action(self, state):

        if self.train:

            if random() < self.epsilon:
                action = choice(self.actions)
            else:
                q = [self.get_Qvalue(state, a) for a in self.actions]
                maxQ = max(q)
                count = q.count(maxQ)

                if count > 1:
                    best = [i for i in range(len(self.actions)) if q[
                        i] == maxQ]
                    i = choice(best)
                else:
                    i = q.index(maxQ)
                action = self.actions[i]

        else:
            q = [self.get_Qvalue(state, a) for a in self.actions]
            maxQ = max(q)
            count = q.count(maxQ)

            if count > 1:
                best = [i for i in range(len(self.actions)) if q[i] == maxQ]
                i = choice(best)
            else:
                i = q.index(maxQ)
            action = self.actions[i]

        return action

    def learn(self, state1, action1, reward, state2):
        maxqnew = max([self.get_Qvalue(state2, a) for a in self.actions])
        self.learnQ(state1, action1, reward, reward + self.gamma * maxqnew)

    def save_model(self, name):
        """
        Saves the Dictionary to a Pickle

        :param name: str
        :return: None
        """
        output = open(self.directory + name + '.pkl', 'wb')
        pickle.dump(self.q, output)
        output.close()

    def load_model(self, name):
        """
        Loads the Dictionary into the Class

        :param name: str
        :return: None
        """
        pkl_file = open(self.directory + name + '.pkl', 'rb')
        self.q = pickle.load(pkl_file)
        pkl_file.close()


class Q_Learning_Epsilon_Decay:
    """
    Epsilon Rate Decay - Over time Agent gets more responsibility for its own actions
    """

    def __init__(self, settings=None):
        """
        :param settings: dictionary of settings
        """
        assert settings is not None, 'Pass the Settings'
        self.q = {}
        self.directory = os.path.join(os.getcwd(), 'Model/NN_Model/')
        self.actions = range(settings['nb_actions'])
        self.alpha = settings['alpha']
        self.epsilon = settings['epsilon']
        self.gamma = settings['gamma']
        self.decay = settings['epsilon_decay']
        self.rate = settings['epsilon_action']
        self.action_count = 0
        self.train = settings['train']

    def get_Qvalue(self, state, action):
        """
        :param state: tuple
        :param action: int
        :return: Q-value (int)
        """
        return self.q.get((state, action), 0.0)

    def learnQ(self, state, action, reward, value):
        old_value = self.q.get((state, action), None)

        if old_value is None:
            self.q[(state, action)] = reward
        else:
            self.q[(state, action)] = old_value + \
                self.alpha * (value - old_value)

    def choose_Action(self, state):
        """
        :param state: tuple
        :return: action value (int)
        """
        self.learn_decay()
        if self.train:

            if random() < self.epsilon:
                action = choice(self.actions)
            else:
                q = [self.get_Qvalue(state, a) for a in self.actions]
                maxQ = max(q)
                count = q.count(maxQ)

                if count > 1:
                    best = [i for i in range(len(self.actions)) if q[
                        i] == maxQ]
                    i = choice(best)
                else:
                    i = q.index(maxQ)
                action = self.actions[i]

        else:
            q = [self.get_Qvalue(state, a) for a in self.actions]
            maxQ = max(q)
            count = q.count(maxQ)

            if count > 1:
                best = [i for i in range(len(self.actions)) if q[i] == maxQ]
                i = choice(best)
            else:
                i = q.index(maxQ)
            action = self.actions[i]

        self.action_count += 1
        return action

    def learn(self, state1, action1, reward, state2):
        maxqnew = max([self.get_Qvalue(state2, a) for a in self.actions])
        self.learnQ(state1, action1, reward, reward + self.gamma * maxqnew)

    def learn_decay(self):
        if self.action_count % self.rate == 0 and self.action_count > 0:
            self.epsilon = self.epsilon * self.decay

    def save_model(self, name):
        """
        Saves the Dictionary to a Pickle

        :param name: str
        :return: None
        """
        output = open(self.directory + name + '.pkl', 'wb')
        pickle.dump(self.q, output)
        output.close()

    def load_model(self, name):
        """
        Loads the Dictionary into the Class

        :param name: str
        :return: None
        """
        pkl_file = open(self.directory + name + '.pkl', 'rb')
        self.q = pickle.load(pkl_file)
        pkl_file.close()


class Q_Neural_Network:
    """
    Deep Q Learning (DQN) -> CNN - RNN - Linear Output
    """

    def __init__(self, settings=None, track_height=None):
        """
        :param settings: dictionary of settings
        :param track_height: int
        """
        assert settings is not None, 'Pass the Settings'
        assert track_height is not None, 'Pass the track height'
        self.q = {}
        self.actions = range(settings['nb_actions'])
        self.alpha = settings['alpha']
        self.epsilon = settings['epsilon']
        self.gamma = settings['gamma']
        self.max_track = track_height
        self.train = settings['train']

        self.observations = []
        self.directory = os.path.join(os.getcwd(), 'Model/NN_Model/')

        # Neural Network Parameters
        config = self.config()
        self.batch_size = config['batch_size']
        self.dropout = config['dropout']
        self.neurons = config['hidden_units']
        self.embedding_size = config['embedding_size']
        self.input_dim = config['input_dim']
        self.filter_length = config['filter_length']
        self.nb_filter = config['nb_filter']
        self.pool_length = config['pool_length']
        self.obs_size = config['obs_size']
        self.update_rate = config['update_rate']

        self.old_state_m1 = None
        self.action_m1 = None
        self.reward_m1 = None

        self.model = self.create_neural_network_rnn
        self.updates = 0

    def config(self):
        """
            Neural Network (RNN) Configuration Settings

        :return: dict
        """
        c = dict(batch_size=8,
                 dropout=0.2,
                 hidden_units=120,
                 obs_size=15000,
                 embedding_size=120,
                 input_dim=30,
                 filter_length=17,
                 nb_filter=150,
                 pool_length=2,
                 update_rate=400)
        return c

    @property
    def create_neural_network_rnn(self):
        """
        Create the Neural Network Model

        :return: Keras Modelh
        """

        model = Sequential()

        # we start off with an efficient embedding layer which maps
        # our vocab indices into embedding_dims dimensions
        model.add(Embedding(12,  # Number of Features from State Space
                            300,  # Vector Size
                            input_length=self.input_dim))

        # we add a Convolution1D, which will learn nb_filter
        # word group filters of size filter_length:
        model.add(Convolution1D(nb_filter=self.nb_filter,
                                filter_length=self.filter_length,
                                border_mode='valid',
                                activation='relu',
                                subsample_length=1))

        # we use standard max pooling (halving the output of the previous
        # layer):
        model.add(MaxPooling1D(pool_length=self.pool_length))
        model.add(Dropout(self.dropout))

        # We flatten the output of the conv layer,
        # so that we can add a vanilla dense layer:
        model.add(Flatten())

        # We add a vanilla hidden layer:
        model.add(Dense(self.neurons))
        model.add(Dropout(self.dropout))
        model.add(Activation('relu'))

        # We project onto a single unit output layer, and squash it with a
        # sigmoid:
        model.add(Dense(len(self.actions)))
        model.add(Activation('linear'))

        model.compile(loss='mse',
                      optimizer=Adadelta(lr=0.00025))

        print(model.summary())

        return model

    def choose_Action(
            self,
            state=None,
            pstate=None,
            paction=None,
            preward=None):
        """
        :param state: tuple
        :param pstate: tuple
        :param paction: int
        :param preward: int
        :return: action value (int)
        """

        if self.train:

            if random() < self.epsilon or len(
                    self.observations) < self.obs_size or pstate is None:
                action = np.random.randint(0, len(self.actions))
            else:
                state = np.concatenate(
                    (list(pstate), list(state))) + 1
                state = np.asarray(state).reshape(1, self.input_dim)
                qval = self.model.predict(state, batch_size=1)
                action = (np.argmax(qval))

        else:
            if self.updates == 0 or pstate is None:
                action = np.random.randint(0, len(self.actions))
                self.updates += 1
            else:
                state = np.concatenate(
                    (list(pstate), list(state))) + 1
                state = np.asarray(state).reshape(1, self.input_dim)
                qval = self.model.predict(state, batch_size=1)
                action = (np.argmax(qval))

        return action

    def update_train(self, p_state, action, p_reward, new_state, terminal):
        """

        :param p_state:
        :param action:
        :param p_reward:
        :param new_state:
        :param terminal:
        """
        self.observations.append((p_state, action, p_reward, new_state))
        self.updates += 1

        if self.updates % self.update_rate == 0 and self.updates > 0:
            old = self.epsilon
            self.epsilon = self.epsilon * (1 - 1e-4)
            logging.info(
                'Changing epsilon from {:.5f} to {:.5f}'.format(
                    old, self.epsilon))
        # Train Model once enough history and every seven actions...
        if len(
                self.observations) >= self.obs_size and self.updates % self.update_rate == 0:

            X_train, y_train = self.process_minibatch(terminal)

            self.model.fit(X_train,
                           y_train,
                           batch_size=self.batch_size,
                           nb_epoch=1,
                           verbose=1,
                           shuffle=True)

            if random() < 0.45:
                self.save_model(name='TempModel')

    def process_minibatch(self, terminal_rewards):
        """
        Creates Training and Labels Arrays

        :param terminal_rewards: list(2x int)
        :return: tuple(np.array) (training data and labels)
        """
        X_train = []
        y_train = []
        val = 0
        for memory in self.observations:
            if val == 0:
                val += 1
                old_state_m1, action_m1, reward_m1, new_state_m1 = memory
            else:
                # Get stored values.
                old_state_m, action_m, reward_m, new_state_m = memory
                # Get prediction on old state.
                input = np.concatenate(
                    (list(old_state_m1), list(old_state_m))) + 1
                old_state_m = input.reshape(1, self.input_dim)
                old_qval = self.model.predict(old_state_m,
                                              batch_size=1,
                                              verbose=0)
                # Get prediction on new state.
                input2 = np.concatenate((old_state_m[
                                        0][-15:], list(new_state_m))) + 1
                new_state_m = input2.reshape(1, self.input_dim)
                newQ = self.model.predict(new_state_m,
                                          batch_size=1,
                                          verbose=0)
                maxQ = np.max(newQ)
                y = np.zeros((1, len(self.actions)))
                y[:] = old_qval[:]

                # Check for terminal state.
                if reward_m not in terminal_rewards:
                    update = (reward_m + (self.gamma * maxQ))
                else:
                    update = reward_m

                y[0][action_m] = update
                X_train.append(old_state_m.reshape(self.input_dim,))
                y_train.append(y.reshape(len(self.actions),))
                self.old_state_m1, self.action_m1, self.reward_m1, new_state_m1 = memory

        # Generate Numpy Arrays
        X_train = np.array(X_train)
        y_train = np.array(y_train)

        return X_train, y_train

    def save_model(self, name):
        """
        Save the Neural Network Model

        :param name: string (save name)
        :return: None
        """
        json_string = self.model.to_json()
        open(
            self.directory +
            name +
            '_architecture.json',
            'w').write(json_string)
        self.model.save_weights(self.directory + name + '_weights.h5',
                                overwrite=True)
        logging.info('Model Saved!')

    def load_model(self, name):
        """
        load Keras model from JSON and weights
        :param name: str
        :return: None (Loads to Self)
        """
        from keras.models import model_from_json
        self.model = model_from_json(
            open(
                self.directory +
                name +
                '_architecture.json').read())
        self.model.load_weights(self.directory + name + '_weights.h5')
        logging.info('Model Loaded!')
