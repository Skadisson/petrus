from pandas import DataFrame
from sklearn import linear_model, gaussian_process, tree, neural_network, naive_bayes, feature_extraction, pipeline
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
        models = self.shotgun_models(x, y)
        model = self.get_highest_scoring_model(models, x, y)
        target_x, target_y = self.frame_data([target_data], target_attribute, source_attributes)
        estimations = model.predict(target_x)
        if estimations is not None and len(estimations) > 0:
            estimation = numpy.average(estimations)
        else:
            estimation = None
        self.cache.add_log_entry(self.__class__.__name__, 'Estimation with model ' + model.__class__.__name__ + ' for ' + str(len(source_data)) + ' tickets is: ' + str(estimation))

        if estimation < 900:
            estimation = 900

        return estimation

    @staticmethod
    def get_highest_scoring_model(models, x, y):

        highest_score = 0
        highest_scoring_model = None
        for model in models:
            score = model.score(x, y)
            if score > highest_score:
                highest_score = score
                highest_scoring_model = model

        return highest_scoring_model

    @staticmethod
    def shotgun_models(x, y):

        kernel = gaussian_process.kernels.DotProduct() + gaussian_process.kernels.WhiteKernel()
        models = [
            gaussian_process.GaussianProcessRegressor(kernel=kernel, random_state=1337).fit(x, y),
            linear_model.LinearRegression(n_jobs=2).fit(x, y),
            tree.DecisionTreeClassifier().fit(x, y),
            tree.DecisionTreeRegressor().fit(x, y),
            tree.ExtraTreeRegressor().fit(x, y),
            naive_bayes.GaussianNB().fit(x, y),
            neural_network.MLPRegressor(
                hidden_layer_sizes=(10,), activation='relu', solver='adam', alpha=0.001, batch_size='auto',
                learning_rate='constant', learning_rate_init=0.01, power_t=0.5, max_iter=1000, shuffle=True,
                random_state=9, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True,
                early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08
            ).fit(x, y),
            linear_model.Lasso(alpha=0.1, copy_X=True, fit_intercept=True, max_iter=1000,
                               normalize=False, positive=False, precompute=False, random_state=None,
                               selection='cyclic', tol=0.0001, warm_start=False).fit(x, y),
            linear_model.ElasticNet().fit(x, y),
            linear_model.SGDRegressor().fit(x, y),
            linear_model.Ridge().fit(x, y),
            linear_model.PassiveAggressiveRegressor().fit(x, y)
        ]

        return models

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

        for i in range(0, 9):
            max_probability = max(probability_list)
            max_index = list(probability_list).index(max_probability)
            text_ids += [keys[max_index]]
            ticket_relevancies.append(max_probability)
            del(keys[max_index])
            del(texts[max_index])
            del(probability_list[max_index])

        return text_ids, ticket_relevancies
