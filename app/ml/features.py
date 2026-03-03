# ml/features.py
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text


class FeatureExtractor:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)

    def get_all_potential_pairs(self, current_user: str) -> pd.DataFrame:
        """
        Одним SQL-запросом получает признаки всех кандидатов для current_user.
        Без N+1.
        """
        query = text("""
            WITH current AS (
                SELECT p.id, p.username, d.age, p.location, d.gender
                FROM profile p
                LEFT JOIN dopinfo d ON p.username = d.username
                WHERE p.username = :current_user
            ),
            candidates AS (
                SELECT p.id, p.username, d.age, p.location, d.gender
                FROM profile p
                LEFT JOIN dopinfo d ON p.username = d.username
                WHERE p.username != :current_user
            )
            SELECT
                c.username                                      AS candidate_username,
                c.age                                          AS candidate_age,
                ABS(COALESCE(cur.age, 0) - COALESCE(c.age, 0)) AS age_diff,
                CASE WHEN cur.location = c.location THEN 1 ELSE 0 END AS same_city,
                CASE
                    WHEN (cur.gender = 'male'   AND c.gender = 'female')
                      OR (cur.gender = 'female' AND c.gender = 'male')
                    THEN 1 ELSE 0
                END AS opposite_gender,
                CASE WHEN m.id IS NOT NULL THEN 1 ELSE 0 END  AS already_matched
            FROM current cur
            CROSS JOIN candidates c
            LEFT JOIN matches m
                ON (m.user_id = cur.id AND m.target_id = c.id)
                OR (m.user_id = c.id   AND m.target_id = cur.id)
        """)

        df = pd.read_sql(query, self.engine, params={"current_user": current_user})
        return df

    def get_training_data(self) -> pd.DataFrame:
        """
        Подготавливает обучающий датасет: признаки пар + метка (1=мэтч, 0=нет).
        Используется в POST /train.
        """
        query = text("""
            WITH pairs AS (
                -- Позитивные примеры: реальные мэтчи
                SELECT
                    p1.username AS user1, p2.username AS user2, 1 AS label
                FROM matches m
                JOIN profile p1 ON p1.id = m.user_id
                JOIN profile p2 ON p2.id = m.target_id

                UNION ALL

                -- Негативные примеры: случайные пары без мэтча
                SELECT
                    p1.username AS user1, p2.username AS user2, 0 AS label
                FROM profile p1
                CROSS JOIN profile p2
                WHERE p1.id < p2.id
                  AND NOT EXISTS (
                      SELECT 1 FROM matches m
                      WHERE (m.user_id = p1.id AND m.target_id = p2.id)
                         OR (m.user_id = p2.id AND m.target_id = p1.id)
                  )
                ORDER BY RANDOM()
                LIMIT (SELECT COUNT(*) * 3 FROM matches)  -- 3x негативных к позитивным
            )
            SELECT
                pa.label,
                ABS(COALESCE(d1.age, 0) - COALESCE(d2.age, 0))  AS age_diff,
                CASE WHEN p1.location = p2.location THEN 1 ELSE 0 END AS same_city,
                CASE
                    WHEN (d1.gender = 'male'   AND d2.gender = 'female')
                      OR (d1.gender = 'female' AND d2.gender = 'male')
                    THEN 1 ELSE 0
                END AS opposite_gender,
                0 AS already_matched  -- при обучении это всегда 0
            FROM pairs pa
            JOIN profile p1 ON p1.username = pa.user1
            JOIN profile p2 ON p2.username = pa.user2
            LEFT JOIN dopinfo d1 ON d1.username = pa.user1
            LEFT JOIN dopinfo d2 ON d2.username = pa.user2
        """)

        df = pd.read_sql(query, self.engine)
        return df