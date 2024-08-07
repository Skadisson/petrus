from pandas import DataFrame
from sklearn import linear_model, tree, naive_bayes, feature_extraction, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bin.service import Cache
from bin.service import Environment
import numpy


class SciKitLearn:
    """Sci Kit Learn ML Stack"""

    def __init__(self):
        self.cache = Cache.Cache()
        self.environment = Environment.Environment()

    def estimate(self, target_data, source_data, target_attribute, source_attributes):

        x, y = self.frame_data(source_data, target_attribute, source_attributes)
        model = self.init_model(x, y)
        target_x, target_y = self.frame_data([target_data], target_attribute, source_attributes)
        estimations = model.predict(target_x)
        if estimations is not None and len(estimations) > 0:
            estimation = numpy.average(estimations)
        else:
            estimation = None
        self.cache.add_log_entry(self.__class__.__name__, 'Estimation with model ' + model.__class__.__name__ + ' for ' + str(len(source_data)) + ' tickets is: ' + str(estimation))

        if estimation < 900 or estimation is None:
            estimation = 900

        return estimation

    @staticmethod
    def init_model(x, y):

        if len(x) > 10:
            model = tree.DecisionTreeClassifier().fit(x, y)
        else:
            model = linear_model.LinearRegression(n_jobs=2).fit(x, y)

        return model

    @staticmethod
    def frame_data(data, target_attribute, source_attributes):

        df_source_attributes = [target_attribute]
        df_source_attributes += source_attributes
        df = DataFrame(data, columns=df_source_attributes)
        df.sort_values(by=df_source_attributes)
        x = df[source_attributes].astype(int)
        y = df[target_attribute].astype(int)

        return x, y

    @staticmethod
    def get_phoenix_suggestion(texts, keys, query):

        docs_new = [query]
        text_ids = []
        ticket_relevancies = []

        text_clf = pipeline.Pipeline([
            ('vect', feature_extraction.text.CountVectorizer()),
            ('tfidf', feature_extraction.text.TfidfTransformer()),
            ('clf', naive_bayes.MultinomialNB()),
        ])
        text_context = text_clf.fit(texts, keys)
        top_suggestion = text_context.predict(docs_new)
        probabilities = text_context.predict_proba(docs_new)
        probability_list = list(probabilities[0])

        top_index = keys.index(top_suggestion[0])
        probability_list[top_index] = 100

        for i in range(0, 3):
            max_probability = max(probability_list)
            max_index = list(probability_list).index(max_probability)
            text_ids += [keys[max_index]]
            ticket_relevancies.append(max_probability)
            del(keys[max_index])
            del(texts[max_index])
            del(probability_list[max_index])

        return text_ids, ticket_relevancies

    @staticmethod
    def get_cosine_suggestion(texts, keys, query):
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        query_vector = vectorizer.transform([query])
        cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        most_similar_docs_indices = cosine_similarities.argsort()[::-1]

        similar_keys = []
        similarities = []
        top_k = 5
        for idx in most_similar_docs_indices[:top_k]:
            similar_keys.append(keys[idx])
            similarities.append(round(cosine_similarities[idx] * 100, 2))

        return similar_keys, similarities
