#!/usr/bin/env python3
"""One-shot DB init: creates all tables and the sqlite-vec virtual table."""
import sqlite3
import sqlite_vec
from pathlib import Path

DB_PATH = Path("data/ets.db")
DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(str(DB_PATH))
conn.enable_load_extension(True)
sqlite_vec.load(conn)
conn.enable_load_extension(False)

conn.executescript("""
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    created_at DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id INTEGER NOT NULL REFERENCES materias(id),
    nome TEXT NOT NULL,
    descricao TEXT,
    nivel TEXT NOT NULL,
    created_at DATETIME DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_nodes_materia ON knowledge_nodes(materia_id, nome);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id INTEGER NOT NULL REFERENCES materias(id),
    iniciada_em DATETIME DEFAULT (datetime('now')),
    finalizada_em DATETIME,
    autoavaliacao INTEGER,
    pendente TEXT,
    status TEXT DEFAULT 'ativa'
);

CREATE TABLE IF NOT EXISTS evidencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    session_id INTEGER REFERENCES study_sessions(id),
    tipo TEXT NOT NULL,
    resultado REAL NOT NULL,
    created_at DATETIME DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_evidencias_node ON evidencias(node_id, created_at);

CREATE TABLE IF NOT EXISTS session_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES study_sessions(id),
    node_id INTEGER REFERENCES knowledge_nodes(id),
    tipo TEXT NOT NULL,
    created_at DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id INTEGER NOT NULL REFERENCES materias(id),
    filename TEXT NOT NULL,
    sha256 TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS material_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER NOT NULL REFERENCES materials(id),
    node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    relevancia REAL DEFAULT 1.0,
    UNIQUE(material_id, node_id)
);

CREATE TABLE IF NOT EXISTS processing_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER NOT NULL REFERENCES materials(id),
    status TEXT DEFAULT 'queued',
    current_step TEXT,
    tentativas INTEGER DEFAULT 0,
    max_tentativas INTEGER DEFAULT 3,
    error_msg TEXT,
    created_at DATETIME DEFAULT (datetime('now')),
    updated_at DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    frente TEXT NOT NULL,
    verso TEXT NOT NULL,
    ease_factor REAL DEFAULT 2.5,
    interval_days INTEGER DEFAULT 1,
    next_review DATETIME DEFAULT (datetime('now')),
    acertos INTEGER DEFAULT 0,
    erros INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id INTEGER NOT NULL REFERENCES materias(id),
    data_prova DATETIME NOT NULL,
    created_at DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    to_node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    tipo TEXT NOT NULL DEFAULT 'hierarquica',
    created_at DATETIME DEFAULT (datetime('now')),
    CHECK(from_node_id != to_node_id),
    UNIQUE(from_node_id, to_node_id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS node_embeddings USING vec0(
    node_id INTEGER PRIMARY KEY,
    embedding float[384]
);
""")
conn.commit()
conn.close()
print(f"DB initialised at {DB_PATH.resolve()}")
