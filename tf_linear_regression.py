# Sebastian Raschka 2014-2016
# mlxtend Machine Learning Library Extensions
#
# Estimator for Linear Regression
# Author: Sebastian Raschka <sebastianraschka.com>
#
# License: BSD 3 clause

from .tf_base import _TfBaseRegressor
import numpy as np
import tensorflow as tf
from time import time


class TfLinearRegression(_TfBaseRegressor):
    """Estimator for Linear Regression in TensorFlow using Gradient Descent.

    Added in version 0.4.1

    """

    def __init__(self, eta=0.1, epochs=50, print_progress=0,
                 random_seed=None, dtype=None):
        """
        Parameters
        ------------
        eta : float (default: 0.01)
            solver rate (between 0.0 and 1.0)
        epochs : int (default: 50)
            Passes over the training dataset.
        print_progress : int (default: 0)
            Prints progress in fitting to stderr
            0: No output
            1: Epochs elapsed and cost
            2: 1 plus time elapsed
            3: 2 plus estimated time until completion
        random_seed : int (default: None)
            Set random state for shuffling and initializing the weights.
        dtype : Array-type (default: None)
            Uses tensorflow.float32 if None.

        Attributes
        -----------
        weights_ : 1d-array, shape=[n_features]
            Model weights after fitting.
        bias_ : 1d-array, shape=[1]
                Bias unit (intercept term)
        cost_ : list
            Sum of mean squared errors (MSE) after each epoch;

        """
        super(TfLinearRegression, self).__init__(print_progress=print_progress,
                                                 random_seed=random_seed)
        self.eta = eta
        self.epochs = epochs
        if dtype is None:
            self.dtype = tf.float32
        else:
            self.dtype = dtype

    def fit(self, X, y, init_weights=True):
        """Learn weight coefficients from training data.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.
        y : array-like, shape = [n_samples]
            Target values.
        init_weights : bool (default: True)
            Reinitialize weights

        Returns
        -------
        self : object

        """
        self._is_fitted = False
        if not (init_weights is None or isinstance(init_weights, bool)):
            raise AttributeError("init_weights must be True or False")
        self._check_arrays(X=X, y=y)
        if self.random_seed:
            np.random.seed(self.random_seed)
        self._fit(X=X, y=y, init_weights=init_weights)
        self._is_fitted = True
        return self

    def _fit(self, X, y, init_weights=True):
        if not hasattr(self, "cost_"):
            self.cost_ = []
        self.cost_ = []
        g_train = tf.Graph()

        with g_train.as_default():
            tf_X = tf.convert_to_tensor(value=X, dtype=self.dtype)

            # the newaxis below is necassary since matmul
            # in self._net_input returns a 2D array, where the
            # predicted values are stored as a column vector with the
            # dimensions [n_samples, 1], rather than a row vector like y
            # with dimensions [n_samples,]
            # this is a workaround to make the expression
            # tf.reduce_mean(tf.square(y_pred - tf_y))
            # work correctly for simple linear regression and multiple
            # linear regression.

            tf_y = tf.convert_to_tensor(value=y[:, np.newaxis],
                                        dtype=self.dtype)

            if init_weights:
                w = tf.Variable(tf.truncated_normal(shape=[X.shape[1], 1],
                                                    seed=self.random_seed,
                                                    dtype=self.dtype),
                                dtype=self.dtype)

                b = tf.Variable(tf.zeros(shape=[1]), dtype=self.dtype)
            else:
                w = tf.Variable(self.weights_[:, np.newaxis],
                                dtype=self.dtype)
                b = tf.Variable(self.bias_, dtype=self.dtype)

            y_pred = self._net_input(tf_X, w, b)
            mse_cost = tf.reduce_mean(tf.square(y_pred - tf_y))
            optimizer = tf.train.GradientDescentOptimizer(
                learning_rate=self.eta)
            train = optimizer.minimize(mse_cost)
            train_init = tf.initialize_all_variables()

        sess = tf.Session(graph=g_train)
        with sess:

            sess.run(train_init)
            self.init_time_ = time()
            for epoch in range(1, self.epochs + 1):
                _, c = sess.run([train, mse_cost])
                self.cost_.append(c)
                self._print_progress(epoch, cost=c)

            self.weights_ = w.eval().flatten()
            self.bias_ = b.eval()

    def predict(self, X):
        """Predict class labels of X.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.

        Returns
        ----------
        class_labels : array-like, shape = [n_samples]
            Predicted class labels.

        """
        self._check_arrays(X)
        if not self._is_fitted:
            raise AttributeError('Model is not fitted, yet.')
        return self._predict(X).flatten()

    def _predict(self, X):
        g_predict = tf.Graph()
        with g_predict.as_default():
            w = tf.convert_to_tensor(value=self.weights_[:, np.newaxis],
                                     dtype=self.dtype)
            b = tf.convert_to_tensor(value=self.bias_, dtype=self.dtype)
            tf_X = tf.convert_to_tensor(value=X, dtype=self.dtype)
            predict_init = tf.initialize_all_variables()

        sess = tf.Session(graph=g_predict)
        with sess:
            sess.run(predict_init)
            return self._net_input(tf_X, w, b).eval()

    def _net_input(self, X, w, b):
        return tf.add(tf.matmul(X, w), b)
