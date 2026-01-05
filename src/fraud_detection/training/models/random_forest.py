from sklearn.ensemble import RandomForestClassifier


def build_random_forest(
    n_estimators: int = 200,
    max_depth: int | None = None,
    min_samples_split: int = 2,
    min_samples_leaf: int = 1,
    class_weight: str | dict | None = "balanced",
    random_state: int = 42,
) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        class_weight=class_weight,
        random_state=random_state,
        n_jobs=-1,
    )
