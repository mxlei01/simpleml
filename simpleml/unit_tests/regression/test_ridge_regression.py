"""Implements TestRidgeRegression Unittest."""

import unittest
import numpy as np
import pandas as pd
from data_extraction.convert_numpy import ConvertNumpy
from machine_learning.regression.ridge_regression import RidgeRegression
from performance_assessment.k_fold_cross_validation import KFoldCrossValidation
from performance_assessment.predict_output import PredictOutput
from performance_assessment.residual_sum_squares import ResidualSumSquares


class TestRidgeRegression(unittest.TestCase):

    """Test for RidgeRegression.

    Uses housing data to test RidgeRegression.

    Statics:
        _multiprocess_can_split_ (bool): Flag for nose tests to run tests in parallel.

    """

    _multiprocess_can_split_ = True

    def setUp(self):
        """Set up for TestRidgeRegression.

        Loads housing data, and creates training and testing data.

        """
        self.convert_numpy = ConvertNumpy()
        self.ridge_regression = RidgeRegression()
        self.predict_output = PredictOutput()
        self.residual_sum_squares = ResidualSumSquares()
        self.k_fold_cross_validation = KFoldCrossValidation()

        # Create a dictionary type to store relevant data types so that our pandas
        # will read the correct information
        dtype_dict = {'bathrooms': float, 'waterfront': int, 'sqft_above': int, 'sqft_living15': float,
                      'grade': int, 'yr_renovated': int, 'price': float, 'bedrooms': float, 'zipcode': str,
                      'long': float, 'sqft_lot15': float, 'sqft_living': float, 'floors': str, 'condition': int,
                      'lat': float, 'date': str, 'sqft_basement': int, 'yr_built': int, 'id': str, 'sqft_lot': int,
                      'view': int}

        # Create a kc_house that encompasses all test and train data
        self.kc_house = pd.read_csv('./unit_tests/test_data/regression/kc_house/kc_house_data.csv',
                                    dtype=dtype_dict)

        # Create a kc_house_test_frame that encompasses only train data
        self.kc_house_train = pd.read_csv('./unit_tests/test_data/regression/kc_house/kc_house_train_data.csv',
                                          dtype=dtype_dict)

        # Create a kc_house_frames that encompasses only test data
        self.kc_house_test = pd.read_csv('./unit_tests/test_data/regression/kc_house/kc_house_test_data.csv',
                                         dtype=dtype_dict)

        # Create a kc_house_train_valid_shuffled that encompasses both train and valid data and shuffled
        self.kc_house_train_valid_shuffled = pd.read_csv('./unit_tests/test_data/regression/'
                                                         'kc_house_with_validation_k_fold/'
                                                         'wk3_kc_house_train_valid_shuffled.csv',
                                                         dtype=dtype_dict)

    def test_01_gradient_descent_no_penalty(self):
        """Tests gradient descent algorithm.

        Tests the result on gradient descent with low penalty.

        """
        # We will use sqft_living for our features
        features = ['sqft_living']

        # Output will use price
        output = ['price']

        # Convert our pandas frame to numpy
        feature_matrix, output = self.convert_numpy.convert_to_numpy(self.kc_house_train, features, output, 1)

        # Create our initial weights
        initial_weights = np.array([0., 0.])

        # Step size
        step_size = 1e-12

        # Max Iterations to Run
        max_iterations = 1000

        # Tolerance
        tolerance = None

        # L2 Penalty
        l2_penalty = 0.0

        # Compute our gradient descent value
        final_weights = self.ridge_regression.gradient_descent(feature_matrix, output,
                                                               {"initial_weights": initial_weights,
                                                                "step_size": step_size,
                                                                "tolerance": tolerance,
                                                                "l2_penalty": l2_penalty,
                                                                "max_iteration": max_iterations})

        # We will use sqft_iving, and sqft_living15
        test_features = ['sqft_living']

        # Output will be price
        test_output = ['price']

        # Convert our test pandas frame to numpy
        test_feature_matrix, test_output = self.convert_numpy.convert_to_numpy(self.kc_house_test, test_features,
                                                                               test_output, 1)

        # Predict the output of test features
        predicted_output = self.predict_output.regression(test_feature_matrix, final_weights)

        # Compute RSS
        rss = self.residual_sum_squares.residual_sum_squares_regression(test_output, predicted_output)

        # Assert that the weights is correct
        self.assertEqual(round(-0.16311351478746433, 5), round(final_weights[0], 5))
        self.assertEqual(round(263.02436896538489, 3), round(final_weights[1], 3))

        # Assert that rss is correct
        self.assertEqual(round(275723632153607.72, -5), round(rss, -5))

    def test_02_gradient_descent_high_penalty(self):
        """Tests gradient descent.

        Tests the result on gradient descent with high penalty.

        """
        # We will use sqft_living for our features
        features = ['sqft_living']

        # Output will use price
        output = ['price']

        # Convert our pandas frame to numpy
        feature_matrix, output = self.convert_numpy.convert_to_numpy(self.kc_house_train, features, output, 1)

        # Create our initial weights
        initial_weights = np.array([0., 0.])

        # Step size
        step_size = 1e-12

        # Max Iterations to Run
        max_iterations = 1000

        # Tolerance
        tolerance = None

        # L2 Penalty
        l2_penalty = 1e11

        # Compute our gradient descent value
        final_weights = self.ridge_regression.gradient_descent(feature_matrix, output,
                                                               {"initial_weights": initial_weights,
                                                                "step_size": step_size,
                                                                "tolerance": tolerance,
                                                                "l2_penalty": l2_penalty,
                                                                "max_iteration": max_iterations})

        # We will use sqft_iving
        test_features = ['sqft_living']

        # Output will be price
        test_output = ['price']

        # Convert our test pandas frame to numpy
        test_feature_matrix, test_output = self.convert_numpy.convert_to_numpy(self.kc_house_test, test_features,
                                                                               test_output, 1)

        # Predict the output of test features

        predicted_output = self.predict_output.regression(test_feature_matrix, final_weights)

        # Compute RSS
        rss = self.residual_sum_squares.residual_sum_squares_regression(test_output, predicted_output)

        # Assert that the weights is correct
        self.assertEqual(round(9.7673000000000005, 5), round(final_weights[0], 5))
        self.assertEqual(round(124.572, 3), round(final_weights[1], 3))

        # Assert that rss is correct
        self.assertEqual(round(694642101500000.0, -5), round(rss, -5))

    def test_03_gradient_descent_multiple_high_penalty(self):
        """Tests gradient descent.

        Tests gradient descent with multiple features, and high penalty.

        """
        # We will use sqft_iving, and sqft_living15
        features = ['sqft_living', 'sqft_living15']

        # Output will use price
        output = ['price']

        # Convert our pandas frame to numpy
        feature_matrix, output = self.convert_numpy.convert_to_numpy(self.kc_house_train, features, output, 1)

        # Create our initial weights
        initial_weights = np.array([0.0, 0.0, 0.0])

        # Step size
        step_size = 1e-12

        # Max Iterations to Run
        max_iterations = 1000

        # Tolerance
        tolerance = None

        # L2 Penalty
        l2_penalty = 1e11

        # Compute our gradient descent value
        final_weights = self.ridge_regression.gradient_descent(feature_matrix, output,
                                                               {"initial_weights": initial_weights,
                                                                "step_size": step_size,
                                                                "tolerance": tolerance,
                                                                "l2_penalty": l2_penalty,
                                                                "max_iteration": max_iterations})

        # We will use sqft_iving, and sqft_living15
        test_features = ['sqft_living', 'sqft_living15']

        # Output will be price
        test_output = ['price']

        # Convert our test pandas frame to numpy
        test_feature_matrix, test_output = self.convert_numpy.convert_to_numpy(self.kc_house_test, test_features,
                                                                               test_output, 1)

        # Predict the output of test features
        predicted_output = self.predict_output.regression(test_feature_matrix, final_weights)

        # Compute RSS
        rss = self.residual_sum_squares.residual_sum_squares_regression(test_output, predicted_output)

        # Assert that the weights is correct
        self.assertEqual(round(6.7429699999999997, 5), round(final_weights[0], 5))
        self.assertEqual(round(91.489000000000004, 3), round(final_weights[1], 3))
        self.assertEqual(round(78.437490333967176, 3), round(final_weights[2], 3))

        # Assert that rss is correct
        self.assertEqual(round(500404800500842.0, -5), round(rss, -5))

        # Look at the first predicted output
        self.assertEqual(round(270453.53000000003, 3), round(predicted_output[0], 3))

        # The first output should be 310000 in the test set
        self.assertEqual(310000.0, test_output[0])

    def test_04_gradient_descent_k_fold(self):
        """Tests gradient descent with K fold cross validation.

        Tests best l2_penalty for ridge regression using gradient descent.

        """
        # We will use sqft_living for our features
        features = ['sqft_living']

        # Output will use price
        output = ['price']

        # Create our initial weights
        initial_weights = np.array([0., 0.])

        # Step size
        step_size = 1e-12

        # Tolerance
        tolerance = None

        # Max Iterations to Run
        max_iterations = 1000

        # Number of Folds
        folds = 10

        # Store Cross Validation results
        cross_validation_results = []

        # We want to test l2 penalty values in [10^1, 10^2, 10^3, 10^4, ..., 10^11]
        for l2_penalty in np.logspace(1, 11, num=11):

            # Create a dictionary of model_parameters
            model_parameters = {'step_size': step_size,
                                'max_iteration': max_iterations,
                                'initial_weights': initial_weights,
                                'tolerance': tolerance,
                                'l2_penalty': l2_penalty}

            # Compute the cross validation results
            cv = self.k_fold_cross_validation.k_fold_cross_validation(folds, self.ridge_regression.gradient_descent,
                                                                      model_parameters, {"data": self.kc_house_train,
                                                                                         "output": output,
                                                                                         "features": features})

            # Append it into the results
            cross_validation_results.append((l2_penalty, cv))

        # Lowest Result
        lowest = sorted(cross_validation_results, key=lambda x: x[1])[0]

        # Assert True that 10000000 is the l2_penalty that gives the lowest cross validation error
        self.assertEqual(10000000.0, lowest[0])

        # Assert True that is the lowest l2_penalty
        self.assertEqual(round(120916225809145.0, 0), round(lowest[1], 0))

    def test_05_gradient_ascent(self):
        """Tests gradient ascent.

        Tests gradient ascent and compare it with known values.

        """
        # We will use sqft_living for our features
        features = ['sqft_living']

        # Output will be price
        output = ['price']

        # Convert our pandas frame to numpy
        feature_matrix, output = self.convert_numpy.convert_to_numpy(self.kc_house_train, features, output, 1)

        # Create our initial weights
        initial_weights = np.array([0., 0.])

        # Step size
        step_size = 1e-12

        # Max Iterations to Run
        max_iterations = 1000

        # Tolerance
        tolerance = None

        # L2 Penalty
        l2_penalty = 0.0

        # Compute our hill climbing value
        final_weights = self.ridge_regression.gradient_ascent(feature_matrix, output,
                                                              {"initial_weights": initial_weights,
                                                               "step_size": step_size,
                                                               "tolerance": tolerance,
                                                               "l2_penalty": l2_penalty,
                                                               "max_iteration": max_iterations})

        # Assert that the weights is correct
        self.assertEqual(round(-7.7535764461428101e+70, -68), round(final_weights[0], -68))
        self.assertEqual(round(-1.9293745396177612e+74, -70), round(final_weights[1], -70))

    def test_07_gradient_ascent_high_tolerance(self):
        """Tests gradient ascent.

        Tests gradient ascent and compare it with known values.

        """
        # We will use sqft_living for our features
        features = ['sqft_living']

        # Output will be price
        output = ['price']

        # Convert our pandas frame to numpy
        feature_matrix, output = self.convert_numpy.convert_to_numpy(self.kc_house_train, features, output, 1)

        # Create our initial weights
        initial_weights = np.array([0., 0.])

        # Step size
        step_size = 1e-12

        # Max Iterations to Run
        max_iterations = 1000

        # Tolerance
        tolerance = 1

        # L2 Penalty
        l2_penalty = 0.0

        # Compute our hill climbing value
        final_weights = self.ridge_regression.gradient_ascent(feature_matrix, output,
                                                              {"initial_weights": initial_weights,
                                                               "step_size": step_size,
                                                               "tolerance": tolerance,
                                                               "l2_penalty": l2_penalty,
                                                               "max_iteration": max_iterations})

        # Assert that the weights is correct
        self.assertEqual(0, round(final_weights[0], -68))
        self.assertEqual(0, round(final_weights[1], -70))

    def test_08_gradient_descent_no_penalty_high_tolerance(self):
        """Tests gradient descent algorithm.

        Tests the result on gradient descent with low penalty.

        """
        # We will use sqft_living for our features
        features = ['sqft_living']

        # Output will use price
        output = ['price']

        # Convert our pandas frame to numpy
        feature_matrix, output = self.convert_numpy.convert_to_numpy(self.kc_house_train, features, output, 1)

        # Create our initial weights
        initial_weights = np.array([0., 0.])

        # Step size
        step_size = 1e-12

        # Max Iterations to Run
        max_iterations = 100000

        # Tolerance
        tolerance = 10000000000

        # L2 Penalty
        l2_penalty = 0.0

        # Compute our gradient descent value
        final_weights = self.ridge_regression.gradient_descent(feature_matrix, output,
                                                               {"initial_weights": initial_weights,
                                                                "step_size": step_size,
                                                                "tolerance": tolerance,
                                                                "l2_penalty": l2_penalty,
                                                                "max_iteration": max_iterations})

        # We will use sqft_iving, and sqft_living15
        test_features = ['sqft_living']

        # Output will be price
        test_output = ['price']

        # Convert our test pandas frame to numpy
        test_feature_matrix, test_output = self.convert_numpy.convert_to_numpy(self.kc_house_test, test_features,
                                                                               test_output, 1)

        # Predict the output of test features
        predicted_output = self.predict_output.regression(test_feature_matrix, final_weights)

        # Compute RSS
        rss = self.residual_sum_squares.residual_sum_squares_regression(test_output, predicted_output)

        # Assert that the weights is correct
        self.assertEqual(round(0.093859999999999999, 5), round(final_weights[0], 5))
        self.assertEqual(round(262.98200000000003, 3), round(final_weights[1], 3))

        # Assert that rss is correct
        self.assertEqual(round(275724298300000.0, -5), round(rss, -5))
