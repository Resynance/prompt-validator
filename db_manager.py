import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os

class DBManager:
    def __init__(self, 
                 dbname=os.getenv("DB_NAME", "prompt_similarity"), 
                 user=os.getenv("DB_USER", "promptmanager"), 
                 password=os.getenv("DB_PASSWORD", ""), 
                 host=os.getenv("DB_HOST", "localhost"), 
                 port=os.getenv("DB_PORT", "5432")):
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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    requirements TEXT NOT NULL DEFAULT '',
                    project_focus TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Migration: Ensure project_focus exists
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='projects' AND column_name='project_focus';")
            if not cur.fetchone():
                cur.execute("ALTER TABLE projects ADD COLUMN project_focus TEXT;")

            # Migration: Ensure requirements is NOT NULL
            cur.execute("SELECT is_nullable FROM information_schema.columns WHERE table_name='projects' AND column_name='requirements';")
            res = cur.fetchone()
            if res and res[0] == 'YES':
                # Update NULLs to empty string first
                cur.execute("UPDATE projects SET requirements = '' WHERE requirements IS NULL;")
                cur.execute("ALTER TABLE projects ALTER COLUMN requirements SET NOT NULL;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS environments (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(project_id, name)
                );
            """)
            
            # Check if prompts table exists and its current dimension
            cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'prompts';")
            exists = cur.fetchone()
            if exists:
                cur.execute("SELECT atttypmod FROM pg_attribute WHERE attrelid = 'prompts'::regclass AND attname = 'embedding';")
                current_dim = cur.fetchone()[0]
                if current_dim != dim and current_dim != -1: # -1 means no dimension specified
                    # We don't automatically drop, but we could if it's empty.
                    # For now, we'll let save_prompt catch the error.
                    pass
            
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS prompts (
                    id SERIAL PRIMARY KEY,
                    environment_id INTEGER REFERENCES environments(id) ON DELETE CASCADE,
                    prompt_text TEXT NOT NULL,
                    embedding vector({dim}),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def reset_prompts_table(self, dim):
        with self.conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS prompts;")
            self._ensure_schema(dim)

    # Project Management
    def create_project(self, name, requirements, project_focus=None):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO projects (name, requirements, project_focus) VALUES (%s, %s, %s) ON CONFLICT (name) DO UPDATE SET requirements = EXCLUDED.requirements, project_focus = EXCLUDED.project_focus RETURNING id;",
                    (name.lower(), requirements, project_focus)
                )
                return cur.fetchone()[0]
        except psycopg2.errors.UndefinedTable:
            self._ensure_schema()
            return self.create_project(name, requirements, project_focus)

    def update_project(self, name, requirements=None, project_focus=None):
        updates = []
        params = []
        if requirements is not None:
            updates.append("requirements = %s")
            params.append(requirements)
        if project_focus is not None:
            updates.append("project_focus = %s")
            params.append(project_focus)
        
        if not updates:
            return
            
        params.append(name.lower())
        query = f"UPDATE projects SET {', '.join(updates)} WHERE name = %s;"
        with self.conn.cursor() as cur:
            cur.execute(query, tuple(params))

    def get_project(self, name):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM projects WHERE name = %s;", (name.lower(),))
            return cur.fetchone()

    # Environment Management
    def create_environment(self, project_name, env_name):
        project = self.get_project(project_name)
        if not project:
            raise ValueError(f"Project '{project_name}' does not exist.")
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO environments (project_id, name) VALUES (%s, %s) ON CONFLICT (project_id, name) DO NOTHING RETURNING id;",
                    (project['id'], env_name.lower())
                )
                res = cur.fetchone()
                if res:
                    return res[0]
                # If already exists, fetch it
                cur.execute("SELECT id FROM environments WHERE project_id = %s AND name = %s;", (project['id'], env_name.lower()))
                return cur.fetchone()[0]
        except psycopg2.errors.UndefinedTable:
            self._ensure_schema()
            return self.create_environment(project_name, env_name)

    def get_environment_by_name(self, project_name, env_name):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT e.*, p.name as project_name, p.requirements
                FROM environments e
                JOIN projects p ON e.project_id = p.id
                WHERE p.name = %s AND e.name = %s;
            """, (project_name.lower(), env_name.lower()))
            return cur.fetchone()

    def save_prompt(self, environment_id, prompt_text, embedding):
        dim = len(embedding)
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO prompts (environment_id, prompt_text, embedding) VALUES (%s, %s, %s) RETURNING id;",
                    (environment_id, prompt_text, embedding)
                )
                return cur.fetchone()[0]
        except psycopg2.errors.UndefinedTable:
            self._ensure_schema(dim)
            return self.save_prompt(environment_id, prompt_text, embedding)
        except psycopg2.Error as e:
            if "dimensions" in str(e).lower():
                raise RuntimeError(f"Dimension mismatch: Your current model uses {dim} dimensions, but the database is configured for a different size. Please reset the prompt database.")
            raise e

    def find_similar(self, environment_id, embedding, threshold=0.9, limit=5):
        dim = len(embedding)
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, prompt_text, created_at, 1 - (embedding <=> %s::vector) AS similarity
                    FROM prompts
                    WHERE environment_id = %s
                    AND 1 - (embedding <=> %s::vector) > %s
                    ORDER BY similarity DESC
                    LIMIT %s;
                """, (embedding, environment_id, embedding, threshold, limit))
                return cur.fetchall()
        except psycopg2.errors.UndefinedTable:
            return []
        except psycopg2.Error as e:
            if "dimensions" in str(e).lower():
                raise RuntimeError(f"Dimension mismatch: Current model uses {dim} dimensions, but database expects a different size. Reset recommended.")
            raise e

    # Deletion
    def delete_project(self, name):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM projects WHERE name = %s;", (name.lower(),))

    def delete_environment(self, project_name, env_name):
        project = self.get_project(project_name)
        if not project:
            return
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM environments WHERE project_id = %s AND name = %s;", (project['id'], env_name.lower()))

    def delete_environment_prompts(self, project_name, env_name):
        env = self.get_environment_by_name(project_name, env_name)
        if not env:
            return
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM prompts WHERE environment_id = %s;", (env['id'],))

    def close(self):
        self.conn.close()
