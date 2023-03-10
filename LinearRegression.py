#encoding=utf8

import os
import itertools
import numpy as np
import FukuML.Utility as utility
import FukuML.MLBase as ml


class LinearRegression(ml.Learner):

    xpsedo = []

    def __init__(self):

        """init"""

        self.status = 'empty'
        self.train_X = []
        self.train_Y = []
        self.W = []
        self.data_num = 0
        self.data_demension = 0
        self.test_X = []
        self.test_Y = []
        self.feature_transform_mode = ''
        self.feature_transform_degree = 1

        self.xpsedo = []

    def load_train_data(self, input_data_file=''):

        '''
        Load train data
        Please check dataset/pocket_pla_binary_train.dat to understand the data format
        Each feature of data x separated with spaces
        And the ground truth y put in the end of line separated by a space
        '''

        self.status = 'load_train_data'

        if (input_data_file == ''):
            input_data_file = os.path.normpath(os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), "dataset/pocket_pla_binary_train.dat"))
        else:
            if (os.path.isfile(input_data_file) is not True):
                print("Please make sure input_data_file path is correct.")
                return self.train_X, self.train_Y

        self.train_X, self.train_Y = utility.DatasetLoader.load(input_data_file)

        return self.train_X, self.train_Y

    def load_test_data(self, input_data_file=''):

        '''
        Load test data
        Please check dataset/pocket_pla_binary_test.dat to understand the data format
        Each feature of data x separated with spaces
        And the ground truth y put in the end of line separated by a space
        '''

        if (input_data_file == ''):
            input_data_file = os.path.normpath(os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), "dataset/pocket_pla_binary_test.dat"))
        else:
            if (os.path.isfile(input_data_file) is not True):
                print("Please make sure input_data_file path is correct.")
                return self.test_X, self.test_Y

        self.test_X, self.test_Y = utility.DatasetLoader.load(input_data_file)

        if (self.feature_transform_mode == 'polynomial') or (self.feature_transform_mode == 'legendre'):
            self.test_X = self.test_X[:, 1:]

            self.test_X = utility.DatasetLoader.featureTransform(
                self.test_X,
                self.feature_transform_mode,
                self.feature_transform_degree
            )

        return self.test_X, self.test_Y

    def init_W(self):

        '''
        Init the W
        Simple way is init W all zeros
        '''

        if (self.status != 'load_train_data') and (self.status != 'train'):
            print("Please load train data first.")
            return self.W

        self.status = 'init'

        self.data_num = len(self.train_Y)
        self.data_demension = len(self.train_X[0])
        self.W = np.zeros(self.data_demension)

        return self.W

    def score_function(self, x, W):
        # need refector

        '''
        Score function to calculate score
        '''

        score = np.inner(x, W)

        return score

    def error_function(self, y_prediction, y_truth):
        # need refector

        '''
        Error function to calculate error
        '''

        error = (y_prediction - y_truth) ** 2

        return error

    def calculate_avg_error(self, X, Y, W):

        return super(LinearRegression, self).calculate_avg_error(X, Y, W)

    def calculate_test_data_avg_error(self):

        return super(LinearRegression, self).calculate_avg_error()

    def calculate_psedo_X(self, X):

        return np.linalg.pinv(X)

    def train(self):

        '''
        Train Linear Regression Algorithm
        From f(x) = WX
        Find best h(x) = WX similar to f(x)
        Output W
        '''

        if (self.status != 'init'):
            print("Please load train data and init W first.")
            return self.W

        self.status = 'train'

        self.xpsedo = self.calculate_psedo_X(self.train_X)
        self.W = np.dot(self.xpsedo, self.train_Y)

        return self.W

    def prediction(self, input_data='', mode='test_data'):

        return super(LinearRegression, self).prediction(input_data, mode)


class BinaryClassifier(LinearRegression):

    xpsedo = []

    def __init__(self):

        """init"""

        self.status = 'empty'
        self.train_X = []
        self.train_Y = []
        self.W = []
        self.data_num = 0
        self.data_demension = 0
        self.test_X = []
        self.test_Y = []
        self.feature_transform_mode = ''
        self.feature_transform_degree = 1

        self.xpsedo = []

    def load_train_data(self, input_data_file=''):

        return super(BinaryClassifier, self).load_train_data(input_data_file)

    def load_test_data(self, input_data_file=''):

        return super(BinaryClassifier, self).load_test_data(input_data_file)

    def init_W(self):

        return super(BinaryClassifier, self).init_W()

    def score_function(self, x, W):

        '''
        Score function to calculate score
        '''

        score = np.sign(np.inner(x, W))

        return score

    def error_function(self, y_prediction, y_truth):
        # need refector

        '''
        Error function to calculate error
        '''

        if y_prediction != y_truth:
            return 1
        else:
            return 0

    def calculate_avg_error(self, X, Y, W):

        return super(BinaryClassifier, self).calculate_avg_error(X, Y, W)

    def calculate_test_data_avg_error(self):

        return super(BinaryClassifier, self).calculate_avg_error()

    def calculate_psedo_X(self, X):

        return super(BinaryClassifier, self).calculate_psedo_X(X)

    def train(self):

        return super(BinaryClassifier, self).train()

    def prediction(self, input_data='', mode='test_data'):

        return super(BinaryClassifier, self).prediction(input_data, mode)


class MultiClassifier(BinaryClassifier):

    class_list = []
    temp_train_X = []
    temp_train_Y = []
    temp_W = {}
    temp_data_num = 0
    decomposition = 'ovo'

    def __init__(self):

        self.status = 'empty'
        self.train_X = []
        self.train_Y = []
        self.W = []
        self.data_num = 0
        self.data_demension = 0
        self.test_X = []
        self.test_Y = []
        self.xpsedo = []
        self.feature_transform_mode = ''
        self.feature_transform_degree = 1

        self.class_list = []
        self.temp_train_X = []
        self.temp_train_Y = []
        self.temp_W = {}
        self.temp_data_num = 0
        self.decomposition = 'ovo'

    def load_train_data(self, input_data_file=''):

        self.status = 'load_train_data'

        if (input_data_file == ''):
            input_data_file = os.path.normpath(os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), "dataset/digits_multiclass_train.dat"))
        else:
            if (os.path.isfile(input_data_file) is not True):
                print("Please make sure input_data_file path is correct.")
                return self.train_X, self.train_Y

        self.train_X, self.train_Y = utility.DatasetLoader.load(input_data_file)

        return self.train_X, self.train_Y

    def load_test_data(self, input_data_file=''):

        if (input_data_file == ''):
            input_data_file = os.path.normpath(os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), "dataset/digits_multiclass_test.dat"))
        else:
            if (os.path.isfile(input_data_file) is not True):
                print("Please make sure input_data_file path is correct.")
                return self.test_X, self.test_Y

        self.test_X, self.test_Y = utility.DatasetLoader.load(input_data_file)

        if (self.feature_transform_mode == 'polynomial') or (self.feature_transform_mode == 'legendre'):
            self.test_X = self.test_X[:, 1:]

            self.test_X = utility.DatasetLoader.featureTransform(
                self.test_X,
                self.feature_transform_mode,
                self.feature_transform_degree
            )

        return self.test_X, self.test_Y

    def init_W(self, mode='normal'):

        self.W = {}

        if (self.status != 'load_train_data') and (self.status != 'train'):
            print("Please load train data first.")
            return self.W

        self.status = 'init'

        self.data_num = len(self.train_Y)
        self.data_demension = len(self.train_X[0])
        self.class_list = list(itertools.combinations(np.unique(self.train_Y), 2))

        for class_item in self.class_list:
            self.W[class_item] = np.zeros(self.data_demension)

        return self.W

    def score_function(self, x, W):

        return super(MultiClassifier, self).score_function(x, W)

    def score_function_all_class(self, x, W):

        score_list = {}
        ovo_vote = []

        for class_item in self.class_list:
            score = self.score_function(x, W[class_item])
            if score == 1:
                score_list[class_item] = class_item[0]
            else:
                score_list[class_item] = class_item[1]
            ovo_vote.append(score_list[class_item])

        return max(set(ovo_vote), key=ovo_vote.count)

    def error_function(self, y_prediction, y_truth):

        return super(MultiClassifier, self).error_function(y_prediction, y_truth)

    def calculate_avg_error(self, X, Y, W):

        return super(MultiClassifier, self).calculate_avg_error(X, Y, W)

    def calculate_avg_error_all_class(self, X, Y, W):

        data_num = len(Y)
        error_num = 0

        for i in range(data_num):
            error_num = error_num + self.error_function(self.score_function_all_class(X[i], W), Y[i])

        avg_error = error_num / float(data_num)

        return avg_error

    def calculate_test_data_avg_error(self):

        return super(MultiClassifier, self).calculate_avg_error()

    def modify_XY(self, X, Y, class_item):

        modify_X = []
        modify_Y = []

        for idx, val in enumerate(Y):
            if val == class_item[0]:
                modify_Y.append(1)
                modify_X.append(X[idx])
            elif val == class_item[1]:
                modify_Y.append(-1)
                modify_X.append(X[idx])

        return np.array(modify_X), np.array(modify_Y)

    def train(self):

        if (self.status != 'init'):
            print("Please load train data and init W first.")
            return self.W

        for class_item in self.class_list:
            self.status = 'init'
            modify_X, modify_Y = self.modify_XY(self.train_X, self.train_Y, class_item)
            self.temp_train_X = self.train_X
            self.temp_train_Y = self.train_Y
            self.train_X = modify_X
            self.train_Y = modify_Y
            self.temp_data_num = self.data_num
            self.data_num = len(self.train_Y)
            self.temp_W = self.W
            self.W = self.temp_W[class_item]
            self.temp_W[class_item] = super(MultiClassifier, self).train()
            self.train_X = self.temp_train_X
            self.train_Y = self.temp_train_Y
            self.temp_train_X = []
            self.temp_train_Y = []
            self.data_num = self.temp_data_num
            self.temp_data_num = 0
            self.W = self.temp_W
            self.temp_W = {}
            print("class %d to %d learned." % (class_item[0], class_item[1]))

        self.status = 'train'

        return self.W

    def prediction(self, input_data='', mode='test_data'):

        prediction = {}
        prediction_list = {}
        prediction_return = 0.0
        ovo_vote = []

        for class_item in self.class_list:
            self.temp_W = self.W
            self.W = self.temp_W[class_item]
            prediction = super(MultiClassifier, self).prediction(input_data, mode)
            if prediction['prediction'] == 1:
                prediction_list[class_item] = class_item[0]
            else:
                prediction_list[class_item] = class_item[1]
            ovo_vote.append(prediction_list[class_item])
            self.W = self.temp_W
            self.temp_W = {}

        prediction_return = max(set(ovo_vote), key=ovo_vote.count)

        return {
            "input_data_x": prediction['input_data_x'],
            "input_data_y": prediction['input_data_y'],
            "prediction": prediction_return,
            "prediction_list": prediction_list,
        }


class Accelerator(object):

    @staticmethod
    def init_W(ml_learner):
        W = []
        linear = BinaryClassifier()
        linear.status = 'init'
        linear.train_X = ml_learner.train_X
        linear.train_Y = ml_learner.train_Y
        linear.data_num = ml_learner.data_num
        linear.data_demension = ml_learner.data_demension
        linear.W = ml_learner.W
        W = linear.train()
        return W
