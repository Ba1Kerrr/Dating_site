# ml/train.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from dotenv import load_dotenv
from ml.features import FeatureExtractor
from ml.model import MatchPredictor

load_dotenv()

FEATURE_COLUMNS = ["age_diff", "same_city", "opposite_gender", "already_matched"]


def prepare_training_data(db_url):
    """Получает данные для обучения через FeatureExtractor"""
    extractor = FeatureExtractor(db_url)
    df = extractor.get_training_data()

    if df.empty:
        return df, np.array([])

    X = df[FEATURE_COLUMNS]
    y = df["label"].values
    return X, y


if __name__ == "__main__":
    db_url = os.environ["DATABASE_ROUTE"]

    print("Подготавливаем данные...")
    X, y = prepare_training_data(db_url)

    if len(X) == 0:
        print("Нет данных для обучения — нужны мэтчи в таблице matches")
        sys.exit(1)

    print(f"Всего примеров:       {len(X)}")
    print(f"Положительных (мэтч): {int(y.sum())}")
    print(f"Отрицательных:        {int((y == 0).sum())}")

    predictor = MatchPredictor()
    predictor.train(X, y)
    print("Готово. Модель сохранена в ml/models/match_predictor.pkl")