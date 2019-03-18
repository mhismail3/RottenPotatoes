import math
import numpy
from numpy import linalg as la
from operator import itemgetter

import Data

class Engine:

    def __init__(self):
        self.data = Data.MovieData()

    def ecludSim(self, inA, inB):
        """
        Return the Euclidean similarity for two vectors
        """
        return 1.0 / (1.0 + la.norm(inA - inB))

    def cosSim(self, a, b):
        """
        Return the Cosine similarity for two vectors
        """
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(a)):
            x = a[i]
            y = b[i]
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        sumxx = math.sqrt(sumxx)
        sumyy = math.sqrt(sumyy)
        return sumxy / (sumxx * sumyy)

    def pearsSim(self, inA, inB):
        """
        Return the Pearson similarity for two vectors
        """
        if len(inA) < 3: return 1.0
        return 0.5 + 0.5 * numpy.corrcoef(inA, inB, rowvar=0)[0][1]

    def intersection(self, lst1, lst2):
        """
        Return a list containing the overlapping elements between
        two input lists
        """
        lst3 = [value for value in lst1 if value in lst2]
        return lst3

    def get_neighbors(self, tfidf, movie_id, k, metric):
        """
        Return the 'k' closest neighbors based on input metric
        :param tfidf: term tf_idf dataframe matrix
        :param movie_id: id of the movie to search for
        :param k: number of neighbors to return
        :param metric: similarity function to use to get closest neighbors
        """
        distances = []
        neighbors = []
        # iterate over every movie entry in tfidf matrix
        for i in range(0, tfidf.shape[0]):
            dist = metric(tfidf[i, :], tfidf[movie_id, :])
            # append movie id and associated distance to distances
            distances.append((i, dist))
        # sort distances based on 'dist' value
        distances.sort(key=itemgetter(1))
        # append first 'k' entries in distances to neighbors
        for x in range(k):
            neighbors.append(distances[x][0])
        return neighbors

    def print_sim(self, terms, mov, mov_id, k, metric=cosSim):
        """
        Gets the 'k' closest neighbors using the get_neighbors() function
        and prints them to the console
        :param terms: DataFrame object to be used to calculate similarity between rows
        :param mov: DataFrame object with movie information
        :param mov_id: ID of movie of interest
        :param k: number of neighbors to print
        :param metric: similarity function to use to get closest neighbors
        """
        # convert terms from DataFrame object to numpy array
        terms_np = numpy.array(terms)
        # convert mov's 'title' column to an array list of movie titles
        mov_arr = mov.loc[:, 'title'].tolist()
        # call get_neighbors() to return array of neighbors
        neighbors = self.get_neighbors(terms_np, mov_id, k, metric)
        print("Selected Movie: \n")
        print(mov_arr[mov_id], '\n')
        print("Top ", k, " Recommended Movies are: \n")
        # print neighbors one by one
        for i in range(0, len(neighbors)):
            print(mov_arr[neighbors[i]], '\n')

    def get_neighbors2(self, mov, movie_id, k):
        """
        Return the 'k' closest neighbors based on keyword similarity in mov DataFrame
        :param mov: DataFrame object with movie information
        :param movie_id: id of the movie to search for
        :param k: number of neighbors to return
        """
        distances = []
        neighbors = []
        # iterate over every movie entry in mov
        for i in range(0, mov.shape[0]):
            dist = len(self.intersection(mov.loc[i, 'keywords'], mov.loc[movie_id, 'keywords']))
            # append movie id and associated distance to distances
            distances.append((i, dist))
        # sort distances based on 'dist' value
        distances.sort(key=itemgetter(1), reverse=True)
        # append first 'k' entries in distances to neighbors, skipping first one
        for x in range(k):
            neighbors.append(distances[x + 1][0])
        return neighbors

    def print_sim2(self, mov, mov_id, k):
        """
        Gets the 'k' closest neighbors using the get_neighbors() function
        and prints them to the console
        :param mov: DataFrame object with movie information
        :param mov_id: ID of movie of interest
        :param k: number of neighbors to return
        """
        # empty return array
        topmovies = []
        # convert mov's 'title' column to an array list of movie titles
        mov_arr = mov.loc[:, 'title'].tolist()
        # call get_neighbors() to return array of neighbors
        neighbors = self.get_neighbors2(mov, mov_id, k)
        for i in range(0, len(neighbors)):
            topmovies.append(mov_arr[neighbors[i]])
        return topmovies

    def get_recommendations(self, title, k):
        """
        Return an array of 'k' movie titles based on simiilarity to input 'title'
        :param title: title of the movie to use
        :param k: number of neighbors to return
        """
        # get index of movie title in data's mov DataFrame
        movie_index = self.data.get_movie_index(title)
        # if entered title doesn't exist in data
        if movie_index == -1: return []
        return self.print_sim2(self.data.mov, movie_index, k)
