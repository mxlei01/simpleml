"""Implements LassoRegression."""

import numpy as np
from performance_assessment.predict_output import PredictOutput


class LassoRegression:

    """Class to compute Lasso Regression.

    Lasso Regression is essentially L1 Norm with Linear Regression. We cannot use gradient descent since the
    absolute value for L1 Norm is not differentiable. Hence we use coordinate descent.

    Attributes:
        predict_output (PredictOutput): A PredictOutput class that can predict output given features and weights.

    """

    def __init__(self):
        """Set up PredictOutput class.

        Constructor for the LassoRegression class, mainly used to setup PredictOutput.

        """
        self.predict_output = PredictOutput()

    def lasso_cyclical_coordinate_descent(self, feature_matrix, output, model_parameters):
        """Coordinate descent algorithm for Lasso regression.

        Performs a Lasso Cyclical Coordinate Descent, which will loop over each features and then perform
        coordinate descent, and if all of the weight changes are less than the tolerance, then we will
        stop.

        Lasso Regression is based on: w_j = ro_j + delta/2  if ro_j < -delta/2
                                           0               if ro_j between [-delta/2,delta/2]
                                           ro_j - delta/2  if ro_j >  delta/2
        Where,
            ro_j = Sigma(N, i=1, h_j(x_i)(y_i-y^_i(w_-j).
            h_j(x_i): Normalized features of x_i (input features, but without j feature).
            y_i: Real output.
            y^_i(w_-j): Predicted output without feature j.

        Args:
            feature_matrix (numpy.ndarray): Feature matrix.
            output (numpy.array): Real output for the feature matrix.
            model_parameters (dict): A dictionary of model parameters,
                {
                    initial_weights (numpy.array): The starting initial weights,
                    step_size (float): Step size,
                    tolerance (float or None): Tolerance (or epsilon),
                    l1_penalty (float): L1 penalty value,
                    max_iteration (int): Maximum iteration to compute.
                }

        Returns:
            numpy.array: final weights after coordinate descent has been completed

        """
        # Flag to indicate that the change is too low
        low_change = False

        # Set Weights to initial_weights
        weights = model_parameters["initial_weights"]

        # While the change is not too low (meaning lower than tolerance)
        while not low_change:

            # An array of boolean to detect if all the changes are less than tolerance
            change = []

            # Need to incorporate all the new changes to the weights
            for i, _ in enumerate(weights):
                # Remember the old weights
                old_weights_i = weights[i]

                # Compute the current weight
                weights[i] = self.lasso_coordinate_descent_step({"i": i, "weights": weights}, feature_matrix, output,
                                                                model_parameters)

                # Returns true if any weight changes greater than tolerance
                change.append(abs(old_weights_i - weights[i]) > model_parameters["tolerance"])

            # Returns true if all the changes are less than tolerance
            low_change = not any(change)

        return weights

    def lasso_coordinate_descent_step(self, step_parameters, feature_matrix, output, model_parameters):
        """Compute the Lasso coordinate descent step.

        Compute the Lasso coordinate descent step, which is essentially computing a new ro_i, and based on the
        index and ro_i, compute new w_i weight.

        Args:
            step_parameters (dict): A dictionary for step data,
                {
                    i (int): Feature i,
                    weights (numpy.array): Current weights.
                }
            feature_matrix (numpy.ndarray): Feature matrix.
            output (numpy.array): Real output for feature_matrix.
            model_parameters (dict): A dictionary of model parameters,
                {
                    step_size (float): Step size,
                    tolerance (float or None): Tolerance (or epsilon),
                    l1_penalty (float): L1 penalty value,
                    max_iteration (int): Maximum iteration to compute.
                }


        Returns:
            new_weight_i (float): New weight for the feature i.

        """
        # compute ro[i] = SUM[ [feature_i]*(output - prediction + weight[i]*[feature_i]) ]
        ro_i = self.compute_ro_j(feature_matrix, output, step_parameters["weights"])[step_parameters["i"]]

        # when i == 0, then it's a intercept -- do not regularize
        # else
        #   w_i = ro_i + delta/2  if ro_i < -delta/2
        #         0               if ro_i between [-delta/2,delta/2]
        #         ro_i - delta/2  if ro_i >  delta/2
        if step_parameters["i"] == 0:
            new_weight_i = ro_i
        elif ro_i < -model_parameters["l1_penalty"] / 2.:
            new_weight_i = ro_i + model_parameters["l1_penalty"] / 2
        elif ro_i > model_parameters["l1_penalty"] / 2.:
            new_weight_i = ro_i - model_parameters["l1_penalty"] / 2
        else:
            new_weight_i = 0.

        # Return the new weight for feature i
        return new_weight_i

    def compute_ro_j(self, feature_matrix, real_output, weights):
        """Compute ro_j.

        Compute ro_j using ro_j = Sigma(N, i=1, h_j(x_i)(y_i-y^_i(w_-j).

        Args:
            feature_matrix (numpy.ndarray): Feature matrix.
            real_output (numpy.array): Real output (not predicted) for feature_matrix.
            weights (numpy.array): The current weights.

        Returns:
            ro (numpy.array): ro (or new weights for each feature).

        """
        # Number of features (columns)
        feature_num = feature_matrix.shape[1]

        # Set ro to be an array that is feature_num size
        ro = np.zeros(feature_num)

        # Loop through feature
        for j in range(feature_num):

            # prediction = y_i(w_-j), prediction without feature j
            prediction = self.predict_output.regression(np.delete(feature_matrix, j, axis=1),
                                                        np.delete(weights, j))

            # residual = output - prediction
            residual = real_output - prediction

            # ro[j] = Sigma(N, i=1, feature_i) * residual
            ro[j] = np.sum([feature_matrix[:, j] * residual])

        return ro
