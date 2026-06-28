"""vec0 virtual table for node embeddings

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-27
"""

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

from alembic import op


def upgrade() -> None:
    op.execute(
        """
        CREATE VIRTUAL TABLE node_embeddings USING vec0(
          node_id INTEGER PRIMARY KEY,
          embedding float[384]
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS node_embeddings")
