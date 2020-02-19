from pandas import DataFrame
from sklearn import linear_model, gaussian_process, tree, naive_bayes, neural_network, feature_extraction
from bin.service import Cache
from bin.service import Environment
from matplotlib import pyplot, colors
import numpy
import os


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

        if estimation < 900:
            estimation = 900

        return estimation

    def generate_plot(self, title, x_attributes, y_attributes, data_sets):

        short_colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'orange']
        plot_path = self.environment.get_path_plot()
        is_existing = os.path.exists(plot_path)
        if is_existing:
            os.remove(plot_path)

        self.generate_pyplot(title, x_attributes, y_attributes, data_sets, short_colors, plot_path, 80)

    def generate_graph(self, title, x_attributes, data_sets):

        all_colors = list(colors.CSS4_COLORS.keys())
        graph_path = self.environment.get_path_graph()
        is_existing = os.path.exists(graph_path)
        if is_existing:
            os.remove(graph_path)

        y_attributes = []
        for data_set in data_sets:
            keys = list(data_set.keys())
            for key in keys:
                if key is not 'Date' and key not in y_attributes:
                    y_attributes.append(key)

        self.generate_pyplot(title, x_attributes, y_attributes, data_sets, all_colors, graph_path, 0)

    @staticmethod
    def generate_pyplot(title, x_attributes, y_attributes, data_sets, short_colors, plot_path, y_lim=0, do_plot=False):

        shape = numpy.pi * 3
        pyplot.figure(num=None, figsize=(12, 8), dpi=96)
        if y_lim > 0:
            pyplot.ylim(0, y_lim)
        pyplot.title(title)

        x_label = ""

        df_data_sets = DataFrame(data_sets)
        x = df_data_sets[x_attributes]
        y = df_data_sets[y_attributes]

        for x_attribute in x_attributes:
            x_label += "{} ".format(x_attribute)
            for y_attribute in y_attributes:
                color = short_colors.pop()
                if do_plot is True:
                    pyplot.plot(x[x_attribute], y[y_attribute], label="{}".format(y_attribute[:8]), c=color, alpha=0.5)
                else:
                    pyplot.scatter(x[x_attribute], y[y_attribute], label="{}".format(y_attribute[:8]), s=shape, c=color, alpha=0.5)

        x_label += " [KW]"

        pyplot.xlabel(x_label)
        pyplot.legend()
        pyplot.savefig(fname=plot_path)
        pyplot.close()

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

    def get_phoenix_suggestion(self, texts, keys, query):
        count_vectorizer = feature_extraction.text.CountVectorizer()
        X_train_counts = count_vectorizer.fit_transform(texts)
        tfidf_transformer = feature_extraction.text.TfidfTransformer()
        X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
        clf = naive_bayes.MultinomialNB().fit(X_train_tfidf, keys)
        docs_new = [query]
        X_new_counts = count_vectorizer.transform(docs_new)
        X_new_tfidf = tfidf_transformer.transform(X_new_counts)
        predicted = clf.predict(X_new_tfidf)
        suggested_key = None
        for doc, category in zip(docs_new, predicted):
            suggested_key = category
        return suggested_key
