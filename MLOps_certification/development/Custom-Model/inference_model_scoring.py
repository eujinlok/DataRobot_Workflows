from builtins import object  # pylint: disable=redefined-builtin
import pickle


class CustomInferenceModel(object):
    """
    This is a template for Python inference model scoring code.
    It loads the custom model pickle, performs any necessary preprocessing or feature engineering,
    and then performs predictions.

    Note: If your model is a binary classification model, you will likely want your predict
           function to use `predict_proba`, whereas for regression you will want to use `predict`
    """

    def __init__(self, path_to_model="custom_model.pickle"):
        """Load the model pickle file."""

        # This supports both Python 2 and 3
        with open(path_to_model, "rb") as picklefile:
            try:
                self.model = pickle.load(picklefile, encoding="latin1")
            except TypeError:
                self.model = pickle.load(picklefile)

    def preprocess_features(self, X):
        """Add any required feature preprocessing here, if it's not handled by the pickled model"""
        return X

    def _determine_positive_class_index(self, positive_class_label):
        """Find index of positive class label to interpret predict_proba output"""
        labels = [str(label) for label in self.model.classes_]
        try:
            return labels.index(positive_class_label)
        except ValueError:
            return 1

    def predict(self, X, positive_class_label=None, negative_class_label=None, **kwargs):
        """
        Predict with the pickled custom model.

        If your model is for classification, you likely want to ensure this function
        calls `predict_proba()`, whereas for regression it should use `predict()`
        """
        X = self.preprocess_features(X)
        if positive_class_label is not None and negative_class_label is not None:
            predictions = self.model.predict_proba(X)
            positive_label_index = self._determine_positive_class_index(positive_class_label)
            negative_label_index = 1 - positive_label_index
            predictions = [
                {
                    positive_class_label: prediction[positive_label_index],
                    negative_class_label: prediction[negative_label_index],
                }
                for prediction in predictions
            ]
        else:
            predictions = [float(prediction) for prediction in self.model.predict(X)]
        return predictions
