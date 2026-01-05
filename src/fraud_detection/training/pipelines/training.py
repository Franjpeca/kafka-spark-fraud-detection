from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from fraud_detection.training.preprocessing.features import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
)


def build_preprocessor() -> ColumnTransformer:
    numeric_transformer = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    return preprocessor


def build_training_pipeline(model) -> Pipeline:
    preprocessor = build_preprocessor()

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline


def train_pipeline(pipeline: Pipeline, X, y) -> Pipeline:
    pipeline.fit(X, y)
    return pipeline


def predict_pipeline(pipeline: Pipeline, X):
    return pipeline.predict(X)
