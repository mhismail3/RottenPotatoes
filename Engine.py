import math
import numpy
#from numpy import *
from numpy import linalg as la
from operator import itemgetter

import Data


class Engine:

    def __init__(self):
        self.data = Data.MovieData()

    def ecludSim(self, inA, inB):
        return 1.0 / (1.0 + la.norm(inA - inB))

    def cosSim(self, a, b):
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
        if len(inA) < 3: return 1.0
        return 0.5 + 0.5 * numpy.corrcoef(inA, inB, rowvar=0)[0][1]

    def intersection(self, lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3

    def get_neighbors(self, tfidf, movie_id, k, metric):
        distances = []
        neighbors = []
        for i in range(0, tfidf.shape[0]):
            dist = metric(tfidf[i, :], tfidf[movie_id, :])
            distances.append((i, dist))
        distances.sort(key=itemgetter(1))
        for x in range(k):
            neighbors.append(distances[x][0])
        return neighbors

    def print_sim(self, terms, mov, mov_id, k, metric=cosSim):
        terms_np = numpy.array(terms)
        mov_arr = mov.loc[:, 'title'].tolist()
        neighbors = self.get_neighbors(terms_np, mov_id, k, metric)
        print("Selected Movie: \n")
        print(mov_arr[mov_id], '\n')
        print("Top ", k, " Recommended Movies are: \n")
        for i in range(0, len(neighbors)):
            print(mov_arr[neighbors[i]], '\n')

    def get_neighbors2(self, mov, movie_id, k):
        distances = []
        neighbors = []
        for i in range(0, mov.shape[0]):
            dist = len(self.intersection(mov.loc[i, 'keywords'], mov.loc[movie_id, 'keywords']))
            distances.append((i, dist))
        distances.sort(key=itemgetter(1), reverse=True)
        for x in range(k):
            neighbors.append(distances[x + 1][0])
        return neighbors

    def print_sim2(self, mov, mov_id, k):
        topmovies = []
        mov_arr = mov.loc[:, 'title'].tolist()
        neighbors = self.get_neighbors2(mov, mov_id, k)
        for i in range(0, len(neighbors)):
            topmovies.append(mov_arr[neighbors[i]])
        return topmovies

    def get_recommendations(self, title, k):
        movie_index = self.data.get_movie_index(title)
        if movie_index == -1: return []
        return self.print_sim2(self.data.mov, movie_index, k)
