import math
import numpy as np
import pandas as pd
from ast import literal_eval
from collections import Counter


class MovieData:

    def __init__(self):
        self.mov = pd.read_csv('data/movies_metadata.csv', na_values=["?"], low_memory=False)
        self.keywords = pd.read_csv('data/keywords.csv', na_values=["?"])
        self.word_list = []
        self.term_freq = pd.DataFrame()
        self.term_tfidf = pd.DataFrame()
        self.preprocess()

    def get_movie_index(self, title):
        if len(self.mov.loc[self.mov['title'] == title]) == 0: return -1;
        return self.mov.loc[self.mov['title'] == title].index.values.astype(int)[0]

    def preprocess(self):
        self.mov = self.mov.drop(columns=['adult', 'belongs_to_collection', 'budget', 'homepage', 'imdb_id',
                                          'original_language', 'poster_path', 'production_companies',
                                          'production_countries', 'revenue', 'runtime', 'spoken_languages',
                                          'status', 'video', 'release_date', 'title'])
        self.mov['id'] = pd.to_numeric(self.mov['id'], errors='coerce')
        self.mov = self.mov.dropna(subset=['id'])
        self.mov['id'] = self.mov['id'].astype('int')
        self.mov = self.mov[
            ['id', 'original_title', 'tagline', 'overview', 'genres', 'popularity', 'vote_average', 'vote_count']]
        self.mov.tagline = self.mov.tagline.fillna('')
        self.mov.overview = self.mov.overview.fillna('')
        self.mov = self.mov.dropna()
        self.mov = self.mov.rename(index=int, columns={'original_title': 'title'})
        self.mov.popularity = self.mov.popularity.astype('float64')
        min_votes = self.mov['vote_count'].quantile(0.90)
        mean_score = float(self.mov['vote_average'].mean())
        self.mov = self.mov.loc[self.mov.vote_count >= min_votes]
        self.mov['scores'] = self.mov.apply(lambda x: (x['vote_count'] / (x['vote_count'] + min_votes) *
                                                       x['vote_average']) + (min_votes / (min_votes + x['vote_count'])
                                                                            * mean_score), axis=1)
        self.mov.drop_duplicates(inplace=True)

        self.mov = self.mov.merge(self.keywords, on='id')

        self.mov['genres'] = self.mov['genres'].apply(literal_eval)
        self.mov['genres'] = self.mov['genres'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
        self.mov['keywords'] = self.mov['keywords'].apply(literal_eval)
        self.mov['keywords'] = self.mov['keywords'].apply(
            lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

        self.word_list = self.mov.apply(lambda x: pd.Series(x['keywords']), axis=1).stack().reset_index(level=1,
                                                                                                        drop=True)
        self.word_list.name = 'keyword'
        self.word_list = self.word_list.value_counts()
        d = self.word_list[self.word_list == 1]
        self.word_list = self.word_list[self.word_list != 1]

        for i in range(0, len(self.mov)):
            words = []
            tmpwords = self.mov.loc[i, 'keywords']
            for j in range(0, len(tmpwords)):
                if tmpwords[j] not in d: words.append(tmpwords[j])
            self.mov.at[i, 'keywords'] = words

    def term_freq(self):
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
        if (self.term_freq.empty): return self.term_tfidf

        n_mov = float(len(self.term_tfidf))
        idfk = pd.DataFrame(index=self.term_tfidf.columns.values, columns=['idfk'])
        for term in self.term_tfidf.columns.values:
            idfk.at[term, 'idfk'] = math.log10(n_mov / float(len(self.term_tfidf.loc[self.term_tfidf[term] != 0.0])))

        for term in self.term_tfidf.columns.values:
            for row in range(0, len(self.term_tfidf)):
                self.term_tfidf.at[row, term] *= idfk.loc[term, 'idfk']

        return self.term_tfidf
