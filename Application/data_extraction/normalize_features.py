import numpy as np


class NormalizeFeatures:
    # Usage:
    #       A class that contains functions to normalize features

    def l2_norm(self, features_matrix):
        # Usage:
        #       Normalize a numpy array using l2 norm: http://mathworld.wolfram.com/L2-Norm.html
        #       also called Euclidean Norm: sqrt(x^2+y^2+z^2)
        # Arguments:
        #       features_matrix (numpy matrix) : a numpy matrix to normalize

        # Compute the 2-norm of each column
        # [norm(X[:,0]), norm(X[:,1]), norm(X[:,2])]
        # Note that for norm, axis=0->column
        #                     axis=1->row
        norms = np.linalg.norm(features_matrix, axis=0)

        # Compute the norm of each column by column/2-norm of column
        # [X[:,0]/norm(X[:,0]), X[:,1]/norm(X[:,1]), X[:,2]/norm(X[:,2])]
        return features_matrix/norms, norms