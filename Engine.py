import math
import numpy
from numpy import linalg as la
from operator import itemgetter

import Data

class Engine:

    def __init__(self):
        self.data = Data.MovieData()

    def ecludSim(a, b):
        """
        Return the Euclidean similarity for two vectors
        """
        return 1.0 / (1.0 + la.norm(a - b))
        
    def cosSim(a, b):
        """
        Return the Cosine similarity for two vectors
        """
        a_norm = la.norm(a)
        b_norm = la.norm(b)
        similarity = numpy.dot(a, b) / (a_norm * b_norm)
        dists = 1 - similarity
        return dists

    def pearsSim(inA, inB):
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
    
    def neighbors_rating(self, ratings, movie_id, k, metric):
        distances = []
        neighbors = []
        # iterate over every movie row in ratings
        for i in range(0, ratings.shape[0]):
            # calculate the distance between selected movie and all others
            dist = metric(ratings[i,:], ratings[movie_id,:])
            # append movie id and associated distance to distances
            distances.append((i, dist))
        # sort distances based on 'dist' value to get closest distance entries
        distances.sort(key=itemgetter(1))
        # append first 'k' entries in distances to neighbors, skipping first one
        for x in range(k):
            neighbors.append(distances[x + 1][0])
        return neighbors
    
    def rec_rating(self, ratings, id_map, mov, mov_id, k, metric=cosSim):
        """
        Gets the 'k' closest neighbors using the neighbors_rating() function
        and prints them to the console
        :param ratings: DataFrame containing all available user ratings for movies,
        where each row is a movie
        :param id_map: DataFrame mapping the indices in ratings DataFrame to movie ID
        :param mov: movie DataFrame containing information on all the movies
        :param mov_id: index ID in mov DataFrame of the movie of interest
        :param k: number of neighbors to return
        :param metric: similarity metric to use in calculating distance between neighbors
        """
        # get actual movie ID based on index inputted as mov_id
        movie_id = mov.loc[mov_id, 'id']
        # get associated ratings index ID from id_map using movie_id
        map_mov_id = id_map.index[id_map['index'] == movie_id].tolist()
        # if id_map didn't contain inputted mov_id, movie doesn't have enough ratings
        # return no neighbors as empty list
        if len(map_mov_id) == 0: return ['insufficient ratings']
        map_mov_id = map_mov_id[0]
        # initialize return variable as empty list
        topmovies = []
        # convert ratings DataFrame to numpy array
        ratings_np = numpy.array(ratings)
        # convert title column from mov DataFrame to a list of movie titles
        mov_arr = mov.loc[:,'title'].tolist()
        # call neighbors_rating() to get back 'k' closest neighbors
        neighbors = self.neighbors_rating(ratings_np, map_mov_id, k, metric)
        # for each entry in neighbors, where an entry is an index ID from the ratings DataFrame
        for i in range(0, len(neighbors)):
            ratings_id = neighbors[i]
            # get the associated true movie ID from id_map based on ratings_id
            ratings_mov_map = id_map.loc[ratings_id, 'index']
            # get the mov index ID from mov DataFrame based on true movie ID
            mov_index_id = mov.index[mov['id'] == ratings_mov_map].tolist()
            # check to make sure mov contains the movie with true movie ID
            if len(mov_index_id) != 0:
                # use mov_index_id to get title of movie from mov_arr and append to topmovies
                topmovies.append(mov_arr[mov_index_id[0]])
            else: topmovies.append('')
        return topmovies

    def neighbors_keyword(self, mov, movie_id, k):
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

    def rec_keyword(self, mov, mov_id, k):
        """
        Gets the 'k' closest neighbors using the neighbors_keywords() function
        and prints them to the console
        :param mov: DataFrame object with movie information
        :param mov_id: ID of movie of interest
        :param k: number of neighbors to return
        :param metric: the similarity metric to use in distance evaluation
        """
        # empty return array
        topmovies = []
        # convert mov's 'title' column to an array list of movie titles
        mov_arr = mov.loc[:, 'title'].tolist()
        # call get_neighbors() to return array of neighbors
        # neighbors contains a list of indices to movies,
        # get the actual movie titles from mov_arr below
        neighbors = self.neighbors_keyword(mov, mov_id, k) 
        for i in range(0, len(neighbors)):
            topmovies.append(mov_arr[neighbors[i]])
        return topmovies


    def get_recommendations(self, title, k, option, metric=cosSim):
        """
        Return an array of 'k' movie titles based on simiilarity to input 'title'
        :param title: title of the movie to use
        :param k: number of neighbors to return
        :param option: can be set based on which type of recommendation the user chooses
        """
        # get index of movie title in data's mov DataFrame
        movie_index = self.data.get_movie_index(title)
        # if entered title doesn't exist in data
        if movie_index == -1: return ['film not found']
        if option == "keywords":
            return self.rec_keyword(self.data.mov, movie_index, k)
        elif option == "ratings":
            return self.rec_rating(self.data.ratings, self.data.r_map, self.data.mov, movie_index, k, metric)
