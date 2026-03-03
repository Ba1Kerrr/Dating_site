# ml/model.py
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import os


class MatchPredictor:
    def __init__(self, model_path="ml/models/match_predictor.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = ["age_diff", "same_city", "opposite_gender", "already_matched"]
        # Пробуем загрузить модель при старте — но не падаем если её нет
        self._try_load()

    def _try_load(self):
        """Тихая загрузка при старте — не падает если файла нет"""
        if os.path.exists(self.model_path):
            try:
                self.load()
                print(f"[ML] Модель загружена из {self.model_path}")
            except Exception as e:
                print(f"[ML] Не удалось загрузить модель: {e}")
        else:
            print("[ML] Файл модели не найден — нужно обучить через POST /train")

    def train(self, X, y):
        """
        X: DataFrame или матрица признаков
        y: целевая переменная (1 - был мэтч, 0 - не было)
        """
        if isinstance(X, pd.DataFrame):
            X = X[self.feature_columns].values

        X_scaled = self.scaler.fit_transform(X)

        # Классификатор вместо регрессора — predict_proba даст честные вероятности
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight="balanced",  # важно если мало позитивных примеров
        )
        self.model.fit(X_scaled, y)
        self.save()

    def predict_proba(self, features_df):
        """
        Возвращает вероятности мэтча (0-1) для каждой строки features_df
        """
        if self.model is None:
            raise ValueError("Модель не обучена. Сначала вызови POST /train")

        X = features_df[self.feature_columns].values
        X_scaled = self.scaler.transform(X)

        # RandomForestClassifier.predict_proba возвращает [[p0, p1], ...]
        # берём вероятность класса 1
        return self.model.predict_proba(X_scaled)[:, 1]

    def save(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "scaler": self.scaler,
                "feature_columns": self.feature_columns,
            },
            self.model_path,
        )
        print(f"[ML] Модель сохранена в {self.model_path}")

    def load(self):
        data = joblib.load(self.model_path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.feature_columns = data["feature_columns"]