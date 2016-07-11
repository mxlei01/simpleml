import unittest
import math
import numpy as np
import pandas as pd
from data_extraction.convert_numpy import ConvertNumpy
from data_extraction.normalize_features import NormalizeFeatures
from machine_learning.regression.lasso_regression.LassoRegression import LassoRegression
from performance_assessment.k_fold_cross_validation import KFoldCrossValidation
from performance_assessment.predict_output import PredictOutput
from performance_assessment.residual_sum_squares import ResidualSumSquares

class TestLassoRegression(unittest.TestCase):
    #   Usage:
    #       Tests for the Lasso Regression Class.

    def setUp(self):
        # Usage:
        #       Constructor for TestLassoRegression
        # Arguments:
        #       None

        # Create an instance of the Convert Numpy class
        self.convert_numpy = ConvertNumpy()

        # Create an instance of the Normalize Features class
        self.normalize_features = NormalizeFeatures()

        # Create an instance of the Lasso Regression class
        self.lasso_regression = LassoRegression()

        # Create an instance of the Predict Output Class
        self.predict_output = PredictOutput()

        # Create an instance of the Residual Sum Squares Class
        self.residual_sum_squares = ResidualSumSquares()

        # Create an instance of the K Fold Cross Validation Class
        self.k_fold_cross_validation = KFoldCrossValidation()

        # Create a dictionary type to store relevant data types so that our pandas
        # will read the correct information
        dtype_dict = {'bathrooms':float, 'waterfront':int, 'sqft_above':int, 'sqft_living15':float,
                      'grade':int, 'yr_renovated':int, 'price':float, 'bedrooms':float, 'zipcode':str,
                      'long':float, 'sqft_lot15':float, 'sqft_living':float, 'floors':str, 'condition':int,
                      'lat':float, 'date':str, 'sqft_basement':int, 'yr_built':int, 'id':str, 'sqft_lot':int,
                      'view':int}

        # Create a kc_house_frame that encompasses all test and train data
        self.kc_house_frame = pd.read_csv('./unit_tests/test_data/kc_house/kc_house_data.csv', dtype=dtype_dict)

        # Create a kc_house_test_frame that encompasses only train data
        self.kc_house_train_frame = pd.read_csv('./unit_tests/test_data/kc_house/kc_house_train_data.csv', dtype=dtype_dict)

        # Create a kc_house_frames that encompasses only test data
        self.kc_house_test_frames = pd.read_csv('./unit_tests/test_data/kc_house/kc_house_test_data.csv', dtype=dtype_dict)

        # Convert all the frames with the floors to float type
        self.kc_house_frame['floors'] = self.kc_house_frame['floors'].astype(float)
        self.kc_house_train_frame['floors'] = self.kc_house_frame['floors'].astype(float)
        self.kc_house_test_frames['floors'] = self.kc_house_frame['floors'].astype(float)

        # Then back to int type
        self.kc_house_frame['floors'] = self.kc_house_frame['floors'].astype(int)
        self.kc_house_train_frame['floors'] = self.kc_house_frame['floors'].astype(int)
        self.kc_house_test_frames['floors'] = self.kc_house_frame['floors'].astype(int)

    def test_01_normalize_features(self):
        # Usage:
        #       Test normalizing features
        # Arguments:
        #       None

        # Normalize the features, and also return the norms
        features, norms = self.normalize_features.l2_norm(np.array([[3., 6., 9.], [4., 8., 12.]]))

        # Assert that the np array is equal to features
        self.assertTrue(np.array_equal(np.array([[0.6, 0.6, 0.6], [0.8, 0.8, 0.8]]), features), True)

        # Assert that the np array is equal to norms
        self.assertTrue(np.array_equal(np.array([5., 10., 15.]), norms), True)

    def test_02_compute_ro(self):
        # Usage:
        #       Test ro computation
        # Arguments:
        #       None

        # We will use sqft_iving, and sqft_living15
        features = ['sqft_living', 'bedrooms']

        # Output will use price
        output = ['price']

        # Convert our pandas frame to numpy
        feature_matrix, output = self.convert_numpy.convert_to_numpy(self.kc_house_frame, features, output, 1)

        # Create our initial weights
        normalized_feature_matrix, norms = self.normalize_features.l2_norm(feature_matrix)

        # Set initial weights
        weights = np.array([1., 4., 1.])

        # Compute ro_j
        ro_j = self.lasso_regression.compute_ro_j(normalized_feature_matrix, output, weights)

        # Assert the output of ro_j
        self.assertTrue(np.allclose(ro_j, np.array([79400300.03492916, 87939470.77299108, 80966698.67596565])))

    def test_03_compute_coordinate_descent_step(self):
        # Usage:
        #       Test coordinate descent step
        # Arguments:
        #       None

        # Assert that both are equal
        self.assertEquals(round(self.lasso_regression.lasso_coordinate_descent_step(1,
                                                                                    np.array([[3./math.sqrt(13),
                                                                                               1./math.sqrt(10)],
                                                                                              [2./math.sqrt(13),
                                                                                               3./math.sqrt(10)]]),
                                                                                    np.array([1., 1.]),
                                                                                    np.array([1., 4.]),
                                                                                    0.1), 8),
                          round(0.425558846691, 8))

    def test_04_coordinate_descent(self):
        # Usage:
        #       Test coordinate descent
        # Arguments:
        #       None

        # We will use sqft_iving, and sqft_living15
        features = ['sqft_living', 'bedrooms']

        # Output will use price
        output = ['price']

        # Convert our pandas frame to numpy
        feature_matrix, output = self.convert_numpy.convert_to_numpy(self.kc_house_frame, features, output, 1)

        # Create our initial weights
        normalized_feature_matrix, norms = self.normalize_features.l2_norm(feature_matrix)

        # Set initial weights
        initial_weights = np.zeros(3)

        # Set l1 penalty
        l1_penalty = 1e7

        # Set tolerance
        tolerance = 1.0

        # Compute the weights using coordinate descent
        weights = self.lasso_regression.lasso_cyclical_coordinate_descent(normalized_feature_matrix, output,
                                                                          initial_weights, l1_penalty, tolerance)

        # Assert that these two numpy arrays are the same
        self.assertTrue(np.allclose(weights, np.array([21624998.3663629, 63157246.78545423, 0.]), True))

        # Predict the output
        predicted_output = self.predict_output.predict_output_regression(normalized_feature_matrix, weights)

        # Assert that the RSS is what we wanted
        self.assertEquals(round(self.residual_sum_squares.residual_sum_squares_regression(output, predicted_output), -10),
                          round(1.63049248148e+15, -10))

    def test_05_coordinate_descent_with_normalization(self):
        # Usage:
        #       Test coordinate descent and then normalize the result, so that we can use
        #       the weights on a test set
        # Arguments:
        #       None

        # We will use multiple features
        features = ['bedrooms',
                    'bathrooms',
                    'sqft_living',
                    'sqft_lot',
                    'floors',
                    'waterfront',
                    'view',
                    'condition',
                    'grade',
                    'sqft_above',
                    'sqft_basement',
                    'yr_built',
                    'yr_renovated']

        # Output will use price
        output = ['price']

        # Convert our pandas frame to numpy
        feature_matrix, output = self.convert_numpy.convert_to_numpy(self.kc_house_train_frame, features, output, 1)

        # Create our initial weights
        normalized_feature_matrix, norms = self.normalize_features.l2_norm(feature_matrix)

        # Compute Multiple Weights
        weights1e7 = self.lasso_regression.lasso_cyclical_coordinate_descent(normalized_feature_matrix, output,
                                                                             np.zeros(len(features)+1), 1e7, 1)
        weights1e8 = self.lasso_regression.lasso_cyclical_coordinate_descent(normalized_feature_matrix, output,
                                                                             np.zeros(len(features)+1), 1e8, 1)
        weights1e4 = self.lasso_regression.lasso_cyclical_coordinate_descent(normalized_feature_matrix, output,
                                                                             np.zeros(len(features)+1), 1e4, 5e5)

        # Compute multiple normalized
        normalized_weights1e4 = weights1e4 / norms
        normalized_weights1e7 = weights1e7 / norms
        normalized_weights1e8 = weights1e8 / norms

        # We will use multiple features
        features = ['bedrooms',
                    'bathrooms',
                    'sqft_living',
                    'sqft_lot',
                    'floors',
                    'waterfront',
                    'view',
                    'condition',
                    'grade',
                    'sqft_above',
                    'sqft_basement',
                    'yr_built',
                    'yr_renovated']

        # Output will use price
        output = ['price']

        # Convert our test pandas frame to numpy
        test_feature_matrix, test_output = self.convert_numpy.convert_to_numpy(self.kc_house_test_frames, features, output, 1)

        # Predict the output
        predicted_output = self.predict_output.predict_output_regression(test_feature_matrix, normalized_weights1e4)

        # Assert that the RSS is what we wanted
        self.assertEquals(round(self.residual_sum_squares.residual_sum_squares_regression(test_output, predicted_output), -12),
                          round(2.2778100476e+14, -12))

        # Predict the output
        predicted_output = self.predict_output.predict_output_regression(test_feature_matrix, normalized_weights1e7)

        # Assert that the RSS is what we wanted
        self.assertEquals(round(self.residual_sum_squares.residual_sum_squares_regression(test_output, predicted_output), -12),
                          round(2.75962079909e+14, -12))

        # Predict the output
        predicted_output = self.predict_output.predict_output_regression(test_feature_matrix, normalized_weights1e8)

        # Assert that the RSS is what we wanted
        self.assertEquals(round(self.residual_sum_squares.residual_sum_squares_regression(test_output, predicted_output), -12),
                          round(5.37049248148e+14, -12))
