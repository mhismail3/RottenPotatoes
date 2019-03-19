
# import necessary libraries
import math
import numpy as np
import pandas as pd
from ast import literal_eval
from collections import Counter


class MovieData:

    def __init__(self):
        # Read in .csv files for movies_metadata and keywords dta
        self.mov = pd.read_csv('data/movies_metadata.csv', na_values=["?"], low_memory=False)
        self.keywords = pd.read_csv('data/keywords.csv', na_values=["?"])
        # self.ratings = pd.read_csv('data/ratings_small.csv', na_values=["?"])
        self.ratings = pd.read_csv('data/ratings.csv', na_values=["?"])
        self.r_map = pd.read_csv('data/ratings_map.csv', na_values=["?"])
        self.word_list = []
        # self.r_map = pd.DataFrame()
        self.term_freq = pd.DataFrame()
        self.term_tfidf = pd.DataFrame()
        
        self.preprocess()

    def get_movie_index(self, title):
        """
        Finds the index of the associated movie title in the mov DataFrame object
        """
        if len(self.mov.loc[self.mov['title'] == title]) == 0: return -1;
        return self.mov.loc[self.mov['title'] == title].index.values.astype(int)[0]

    def preprocess(self):
        """
        Preprocesses the data
        """
        # Drop unused columns from DataFrame
        self.mov = self.mov.drop(columns=['adult', 'belongs_to_collection', 'budget', 'homepage', 'imdb_id',
                                          'original_language', 'poster_path', 'production_companies',
                                          'production_countries', 'revenue', 'runtime', 'spoken_languages',
                                          'status', 'video', 'release_date', 'title'])
        # convert ID column to numeric, keeping any errors as NaN values
        self.mov['id'] = pd.to_numeric(self.mov['id'], errors='coerce')
        # drop NaN values from ID column
        self.mov = self.mov.dropna(subset=['id'])
        # Convert remaining entries in ID column to ints
        self.mov['id'] = self.mov['id'].astype('int')
        # Rearrange column order
        self.mov = self.mov[
            ['id', 'original_title', 'tagline', 'overview', 'genres', 'popularity', 'vote_average', 'vote_count']]
        # Replace NaN values in 'tagline' and 'overview' columns with empty string
        self.mov.tagline = self.mov.tagline.fillna('')
        self.mov.overview = self.mov.overview.fillna('')
        # Drop remaining rows with NaN values. No more NaN values exist in table
        self.mov = self.mov.dropna()
        # Rename column
        self.mov = self.mov.rename(index=int, columns={'original_title': 'title'})
        # Change popularity column to type float
        self.mov.popularity = self.mov.popularity.astype('float64')
        
        # Remove entries with too few votes based on quantile value
        min_votes = self.mov['vote_count'].quantile(0.90)
        mean_score = float(self.mov['vote_average'].mean())
        self.mov = self.mov.loc[self.mov.vote_count >= min_votes]
        self.mov['scores'] = self.mov.apply(lambda x: (x['vote_count'] / (x['vote_count'] + min_votes) *
                                                       x['vote_average']) + (min_votes / (min_votes + x['vote_count'])
                                                                            * mean_score), axis=1)
        # Drop any duplicate rows
        self.mov.drop_duplicates(inplace=True)
        
        # Add keywords from keywords dataframe to new column in mov
        self.mov = self.mov.merge(self.keywords, on='id')

        # Parse stringified JSON in 'genres' and 'keywords' columns to get array of dicts
        # Get only keywords from array of dicts for each column
        self.mov['genres'] = self.mov['genres'].apply(literal_eval)
        self.mov['genres'] = self.mov['genres'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
        self.mov['keywords'] = self.mov['keywords'].apply(literal_eval)
        self.mov['keywords'] = self.mov['keywords'].apply(
            lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

        # Compile list of all keywords
        self.word_list = self.mov.apply(lambda x: pd.Series(x['keywords']), axis=1).stack().reset_index(level=1,
                                                                                                        drop=True)
        self.word_list.name = 'keyword'
        self.word_list = self.word_list.value_counts()
        # d is an array of all keywords that occur only once
        d = self.word_list[self.word_list == 1]
        # Reassign word_list to be itself minus all entried in 'd'
        self.word_list = self.word_list[self.word_list != 1]

        # For every entry in mov DF, remove from 'keywords' column any words in d
        for i in range(0, len(self.mov)):
            words = []
            tmpwords = self.mov.loc[i, 'keywords']
            for j in range(0, len(tmpwords)):
                if tmpwords[j] not in d: words.append(tmpwords[j])
            self.mov.at[i, 'keywords'] = words
        
        # The following code can be used to preprocess the original ratings.csv dataset
        # from the database. Because the preprocessing takes a long time, the preprocessed
        # data is included as 'ratings.csv' and imported in the __init__() function above
        
#        self.ratings = self.ratings.drop(columns=['timestamp'])
#        self.ratings = self.ratings.rename(index=int, columns={'movieId': 'id'})
#        self.ratings = self.ratings.rename(index=int, columns={'userId': 'user_id'})
#
#        movcols = self.mov.loc[:,'id'].tolist()
#        ratings_tmp = pd.DataFrame(index=range(1,self.ratings.user_id.max()+1))
#        for i in range(0, len(self.ratings)):
#            if self.ratings.loc[i, 'id'] in movcols:
#                ratings_tmp.at[self.ratings.loc[i, 'user_id'], self.ratings.loc[i, 'id']] = self.ratings.loc[i, 'rating']
#        self.ratings = ratings_tmp
#         
#        for i in range(0, len(self.ratings.columns)):
#            self.ratings.iloc[:,i] = self.ratings.iloc[:,i].fillna(self.ratings.iloc[:,i].mean())
#        self.ratings = self.ratings.T
#        self.ratings = self.ratings.reset_index()
#        self.ratings = self.ratings.rename(index=int, columns={'level_0': 'id'})
#        
#        self.r_map = pd.DataFrame(index=range(0, len(self.ratings)))
#        self.r_map['index'] = self.ratings['index']
#
#        self.ratings = self.ratings.drop(columns=['index'])

    def term_freq(self):
        """
        Calculate term frequency matrix
        """
        # Create empty DataFrame with number of rows=number of movies and
        # columns as the keywords in self.word_list
        self.term_freq = pd.DataFrame(index=range(0, len(self.mov)), columns=self.word_list.keys())

        # create term frequency matrix
        col_terms = self.term_freq.columns.values
        for row in range(0, len(self.term_freq)):
            row_keywords = self.mov.loc[row, 'keywords']
            count = Counter(row_keywords)
            for col in range(0, len(self.term_freq.columns)):
                if col_terms[col] in row_keywords:
                    self.term_freq.at[row, col_terms[col]] = count[col_terms[col]]
                else:
                    self.term_freq.at[row, col_terms[col]] = 0
        self.term_freq = self.term_freq.astype('float64')
        return self.term_freq

    def term_tfidf(self):
        """
        Calculate term tf_idf matrix from term_freq DataFrame
        """
        # If term_freq hasn't been calculated yet
        if (self.term_freq.empty): return self.term_tfidf

        # Use tf_idf equation below to calculate and repopulate term_tfidf DF
        n_mov = float(len(self.term_tfidf))
        idfk = pd.DataFrame(index=self.term_tfidf.columns.values, columns=['idfk'])
        for term in self.term_tfidf.columns.values:
            idfk.at[term, 'idfk'] = math.log10(n_mov / float(len(self.term_tfidf.loc[self.term_tfidf[term] != 0.0])))

        for term in self.term_tfidf.columns.values:
            for row in range(0, len(self.term_tfidf)):
                self.term_tfidf.at[row, term] *= idfk.loc[term, 'idfk']

        return self.term_tfidf
