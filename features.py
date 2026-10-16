def pdays_features(X):
    X = X.copy()
    X["pdays_never"] = (X["pdays"] == 999).astype(int)
    X["pdays"] = X["pdays"].where(X["pdays"] != 999, 0)
    return X
