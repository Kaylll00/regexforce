"""Create RegexForge persistence tables."""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    for table, columns in {
        "rules": [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("kind", sa.String(length=30), nullable=False),
            sa.Column("definition", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        ],
        "test_sets": [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("strings", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        ],
        "analysis_reports": [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("kind", sa.String(length=100), nullable=False),
            sa.Column("input_refs", sa.JSON(), nullable=False),
            sa.Column("result", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        ],
    }.items():
        op.create_table(table, *columns)


def downgrade() -> None:
    op.drop_table("analysis_reports")
    op.drop_table("test_sets")
    op.drop_table("rules")
    op.drop_table("projects")
