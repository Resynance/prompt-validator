import psycopg2
from psycopg2.extras import RealDictCursor
import json

class DBManager:
    def __init__(self, dbname="prompt_similarity", user="maxturner", password="", host="localhost", port="5432"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.conn.autocommit = True

    def _ensure_schema(self, dim=1536):
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS prompts (
                    id SERIAL PRIMARY KEY,
                    project TEXT NOT NULL,
                    prompt_text TEXT NOT NULL,
                    embedding vector({dim}),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def save_prompt(self, project, prompt_text, embedding):
        dim = len(embedding)
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO prompts (project, prompt_text, embedding) VALUES (%s, %s, %s) RETURNING id;",
                    (project, prompt_text, embedding)
                )
                return cur.fetchone()[0]
        except psycopg2.errors.UndefinedTable:
            self._ensure_schema(dim)
            return self.save_prompt(project, prompt_text, embedding)
        except Exception as e:
            if "different dimensions" in str(e):
                # If dimensions changed, we might need to alert the user or handle it.
                # For now, we'll just raise it.
                raise e
            raise e

    def find_similar(self, project, embedding, threshold=0.9, limit=5):
        dim = len(embedding)
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Using cosine similarity: 1 - (embedding <=> target)
                # <=> is cosine distance in pgvector
                cur.execute("""
                    SELECT id, project, prompt_text, 1 - (embedding <=> %s::vector) AS similarity
                    FROM prompts
                    WHERE project = %s
                    AND 1 - (embedding <=> %s::vector) > %s
                    ORDER BY similarity DESC
                    LIMIT %s;
                """, (embedding, project, embedding, threshold, limit))
                return cur.fetchall()
        except psycopg2.errors.UndefinedTable:
            return []
        except Exception as e:
            raise e

    def close(self):
        self.conn.close()
