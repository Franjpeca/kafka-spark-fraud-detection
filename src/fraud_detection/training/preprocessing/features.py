# src/fraud_detection/training/preprocessing/features.py

# -------------------------------
# Target
# -------------------------------
TARGET_COLUMN = "isFraud"

# -------------------------------
# Feature groups
# -------------------------------
NUMERICAL_FEATURES = [
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
]

CATEGORICAL_FEATURES = [
    "type",
]

# -------------------------------
# All model features
# -------------------------------
MODEL_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
