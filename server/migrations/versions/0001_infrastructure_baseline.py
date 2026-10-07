"""infrastructure baseline (no business tables)

Establishes the shared migration head that every future feature-module migration
branches from. Intentionally empty: Module M owns no business entities, so this
revision creates no tables.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-10-07
"""

from __future__ import annotations

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """No-op. Infrastructure baseline only."""
    pass


def downgrade() -> None:
    """No-op. Infrastructure baseline only."""
    pass
