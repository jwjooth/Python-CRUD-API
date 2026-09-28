"""One-off database migrations.

Run one with `python -m migrations.<module>` while application writers are
stopped. There is no migration framework in this project: `create_all` builds
fresh databases and these scripts upgrade existing ones.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def run(upgrade: Callable[[Engine], None]) -> None:
    """Apply a migration to the engine configured in `database.py`."""
    from database import engine

    logger.info("running %s", upgrade.__module__)
    upgrade(engine)
    logger.info("%s completed", upgrade.__module__)
