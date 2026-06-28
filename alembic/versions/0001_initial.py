"""initial

Revision ID: 0001
Revises:
Create Date: 2026-06-27

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("PRAGMA journal_mode=WAL")
    op.execute("PRAGMA foreign_keys=ON")

    op.create_table(
        "materias",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nome", sa.Text, nullable=False, unique=True),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "knowledge_nodes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("materia_id", sa.Integer, sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("nome", sa.Text, nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("nivel", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_knowledge_nodes_materia_id_nome", "knowledge_nodes", ["materia_id", "nome"])

    op.create_table(
        "dependencies",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("from_node_id", sa.Integer, sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("to_node_id", sa.Integer, sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("tipo", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.CheckConstraint("from_node_id != to_node_id", name="ck_dependencies_no_self_ref"),
        sa.UniqueConstraint("from_node_id", "to_node_id", name="uq_dependencies_pair"),
    )

    op.create_table(
        "study_sessions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("materia_id", sa.Integer, sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("iniciada_em", sa.DateTime, server_default=sa.func.now()),
        sa.Column("finalizada_em", sa.DateTime, nullable=True),
        sa.Column("autoavaliacao", sa.Integer, nullable=True),
        sa.Column("pendente", sa.Text, nullable=True),
        sa.Column("status", sa.Text, server_default="ativa"),
    )

    op.create_table(
        "evidencias",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("node_id", sa.Integer, sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("study_sessions.id"), nullable=True),
        sa.Column("tipo", sa.Text, nullable=False),
        sa.Column("resultado", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_evidencias_node_id_created_at", "evidencias", ["node_id", "created_at"])

    op.create_table(
        "session_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("study_sessions.id"), nullable=False),
        sa.Column("node_id", sa.Integer, sa.ForeignKey("knowledge_nodes.id"), nullable=True),
        sa.Column("tipo", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "materials",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("materia_id", sa.Integer, sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("filename", sa.Text, nullable=False),
        sa.Column("sha256", sa.Text, nullable=False, unique=True),
        sa.Column("path", sa.Text, nullable=False),
        sa.Column("status", sa.Text, server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "material_nodes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("material_id", sa.Integer, sa.ForeignKey("materials.id"), nullable=False),
        sa.Column("node_id", sa.Integer, sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("relevancia", sa.Float, server_default="1.0"),
        sa.UniqueConstraint("material_id", "node_id", name="uq_material_nodes_pair"),
    )

    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("material_id", sa.Integer, sa.ForeignKey("materials.id"), nullable=False),
        sa.Column("status", sa.Text, server_default="queued"),
        sa.Column("current_step", sa.Text, nullable=True),
        sa.Column("tentativas", sa.Integer, server_default="0"),
        sa.Column("max_tentativas", sa.Integer, server_default="3"),
        sa.Column("error_msg", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "flashcards",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("node_id", sa.Integer, sa.ForeignKey("knowledge_nodes.id"), nullable=False),
        sa.Column("frente", sa.Text, nullable=False),
        sa.Column("verso", sa.Text, nullable=False),
        sa.Column("ease_factor", sa.Float, server_default="2.5"),
        sa.Column("interval_days", sa.Integer, server_default="1"),
        sa.Column("next_review", sa.DateTime, server_default=sa.func.now()),
        sa.Column("acertos", sa.Integer, server_default="0"),
        sa.Column("erros", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "exams",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("materia_id", sa.Integer, sa.ForeignKey("materias.id"), nullable=False),
        sa.Column("data_prova", sa.DateTime, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("exams")
    op.drop_table("flashcards")
    op.drop_table("processing_jobs")
    op.drop_table("material_nodes")
    op.drop_table("materials")
    op.drop_table("session_events")
    op.drop_index("ix_evidencias_node_id_created_at", "evidencias")
    op.drop_table("evidencias")
    op.drop_table("study_sessions")
    op.drop_table("dependencies")
    op.drop_index("ix_knowledge_nodes_materia_id_nome", "knowledge_nodes")
    op.drop_table("knowledge_nodes")
    op.drop_table("materias")
