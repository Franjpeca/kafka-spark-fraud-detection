from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

import mlflow
import mlflow.sklearn

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))


from fraud_detection.config.config_loader import get_config
from fraud_detection.utils.logging_setup import get_logger

from fraud_detection.training.data.load import load_paysim
from fraud_detection.training.preprocessing.features import (
    MODEL_FEATURES,
    TARGET_COLUMN,
)
from fraud_detection.training.models.random_forest import build_random_forest
from fraud_detection.training.pipelines.training import build_training_pipeline
from fraud_detection.training.evaluation.metrics import (
    compute_classification_metrics,
)



logger = get_logger(service_name="training")


def main():
    logger.info("=== INICIO TRAINING JOB ===")

    cfg = get_config()

    dataset_path = cfg["paths"]["data_raw"]["datasets"]["paysim_train"]
    test_size = cfg.get("training", {}).get("test_size", 0.2)
    random_state = cfg.get("training", {}).get("random_state", 42)

    mlflow_tracking_uri = cfg.get("mlflow", {}).get(
        "tracking_uri", "http://localhost:5000"
    )
    experiment_name = cfg.get(
        "mlflow", {}
    ).get("experiment_name", "fraud_detection_baseline")

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)

    logger.info(f"Cargando dataset de training: {dataset_path}")
    df = load_paysim(dataset_path)

    logger.info("Separando features y target")
    X = df[MODEL_FEATURES]
    y = df[TARGET_COLUMN]

    logger.info("Split train / test")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    with mlflow.start_run(run_name="random_forest_baseline"):

        mlflow.log_param("model_type", "random_forest")
        mlflow.log_param("test_size", test_size)
        mlflow.log_param("random_state", random_state)

        logger.info("Construyendo modelo Random Forest")
        model = build_random_forest(random_state=random_state)

        rf_params = model.get_params()
        for k, v in rf_params.items():
            mlflow.log_param(f"rf__{k}", v)

        logger.info("Construyendo pipeline")
        pipeline = build_training_pipeline(model)

        logger.info("Entrenando pipeline")
        pipeline.fit(X_train, y_train)

        logger.info("Evaluando modelo")
        y_pred = pipeline.predict(X_test)

        if hasattr(pipeline.named_steps["model"], "predict_proba"):
            y_proba = pipeline.predict_proba(X_test)[:, 1]
        else:
            y_proba = None

        metrics = compute_classification_metrics(
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_proba,
        )

        for k, v in metrics.items():
            mlflow.log_metric(k, v)
            logger.info(f"{k}: {v:.4f}")

        logger.info("Guardando pipeline entrenado en MLflow")
        mlflow.sklearn.log_model(
            pipeline,
            artifact_path="model",
            registered_model_name="fraud_detection_random_forest",
        )

    logger.info("=== FIN TRAINING JOB ===")


if __name__ == "__main__":
    main()
