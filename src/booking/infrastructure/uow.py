from __future__ import annotations

from types import TracebackType
from typing import Optional, Type

from sqlalchemy.orm import Session, sessionmaker

from booking.application.unit_of_work import UnitOfWork
from booking.infrastructure.repositories import (
    InMemoryReservationRepository,
    InMemoryTablesRepository,
    SqlAlchemyReservationRepository,
    SqlAlchemyTablesRepository,
)


class InMemoryUnitOfWork(UnitOfWork):
    """UoW для тестов/демо без БД."""

    def __init__(self) -> None:
        self.reservations = InMemoryReservationRepository()
        self.tables = InMemoryTablesRepository()
        self.committed = False

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        if exc_type:
            self.rollback()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False


# Заготовка под SQLAlchemy UoW (для лекции / дальнейшего расширения)
class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory
        self.session: Optional[Session] = None
        self.reservations: Optional[SqlAlchemyReservationRepository] = None
        self.tables: Optional[SqlAlchemyTablesRepository] = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        self.reservations = SqlAlchemyReservationRepository(self.session)
        self.tables = SqlAlchemyTablesRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

    def commit(self) -> None:
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()
