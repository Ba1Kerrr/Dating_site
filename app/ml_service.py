from fastapi import FastAPI, HTTPException
from ml.features import FeatureExtractor
from ml.model import MatchPredictor
import os

app = FastAPI()

db_url = os.getenv("DATABASE_ROUTE")
extractor = FeatureExtractor(db_url)
predictor = MatchPredictor()


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": predictor.model is not None}


@app.post("/train")
async def train_model():
    """Обучает модель на данных из БД"""
    try:
        from ml.train import prepare_training_data
        X, y = prepare_training_data(db_url)

        if len(X) == 0:
            raise HTTPException(status_code=400, detail="Нет данных для обучения — нужны мэтчи в БД")

        predictor.train(X, y)
        return {
            "status": "trained",
            "samples": len(X),
            "positive": int(y.sum()),
            "negative": int((y == 0).sum()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rank")
async def rank_candidates(data: dict):
    """Ранжирует кандидатов для текущего пользователя"""
    current_user = data.get("current_user")
    candidates = data.get("candidates", [])

    if not current_user:
        raise HTTPException(status_code=400, detail="current_user обязателен")

    if predictor.model is None:
        # Если модель не обучена — возвращаем кандидатов в исходном порядке
        return {"ranked_candidates": [{"username": c, "score": 0.5} for c in candidates]}

    try:
        features_df = extractor.get_all_potential_pairs(current_user)

        if features_df.empty:
            return {"ranked_candidates": []}

        # Фильтруем только запрошенных кандидатов
        if candidates:
            features_df = features_df[features_df["candidate_username"].isin(candidates)]

        if features_df.empty:
            return {"ranked_candidates": []}

        scores = predictor.predict_proba(features_df)
        features_df = features_df.copy()
        features_df["score"] = scores

        ranked = (
            features_df.sort_values("score", ascending=False)[["candidate_username", "score"]]
            .rename(columns={"candidate_username": "username"})
            .to_dict("records")
        )

        return {"ranked_candidates": ranked}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))