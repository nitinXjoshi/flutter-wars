"""Shared SQLModel metadata registry for Alembic (Module M).

This is the single place feature modules plug into the shared migration workflow.
Module M does not import business code; each SQLModel-owning module adds its
model module import path below so its tables become visible to Alembic.

Adding a module (see docs/migrations.md):

    FEATURE_MODEL_MODULES = (
        "app.modules.catalog.models",   # Module D - Widget Catalog
        "app.modules.ledger.models",    # Module E - Credit Ledger
        ...
    )

Until feature modules exist the tuple is empty, so the migration history contains
only the infrastructure baseline.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy import MetaData

FEATURE_MODEL_MODULES: tuple[str, ...] = (
    # "app.modules.<module>.models",  # added by each SQLModel-owning module
)


def load_metadata() -> "MetaData":
    """Import every registered model module and return the shared SQLModel metadata."""
    for module_name in FEATURE_MODEL_MODULES:
        importlib.import_module(module_name)

    from sqlmodel import SQLModel

    return SQLModel.metadata
