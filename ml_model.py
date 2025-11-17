# ml_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from data_generation import generate_training_data

def train_multi_algo_model(samples=1000):
    df = generate_training_data(samples)
    X = df[["Page", "SeqLen", "Frames", "InMemory", "Recency", "FutureFreq", "Algorithm"]]
    X = pd.get_dummies(X, columns=["Algorithm"])
    y = df["PageFault"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    return model, acc
