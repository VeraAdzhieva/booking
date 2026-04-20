from __future__ import annotations

from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from booking.domain.model import (
    PartySize,
    Reservation,
    ReservationAggregate,
    ReservationStatus,
    TableId,
    TimeSlot,
)
from booking.domain.repository import ReservationRepository, TablesRepository
from booking.infrastructure.database.model import ReservationDBModel, TableDBModel


class InMemoryReservationRepository(ReservationRepository):
    def __init__(self) -> None:
        self._items: dict[str, ReservationAggregate] = {}

    def get(self, reservation_id: str) -> Optional[ReservationAggregate]:
        return self._items.get(reservation_id)

    def save(self, reservation_agg: ReservationAggregate) -> None:
        self._items[reservation_agg.root.id] = reservation_agg

    def add(self, reservation_agg: ReservationAggregate) -> None:
        self._items[reservation_agg.root.id] = reservation_agg

    def list_for_slot(self, slot: TimeSlot) -> List[ReservationAggregate]:
        for agg in self._items.values():
            busy = []
            exist_slot = agg.root.slot
            if exist_slot.start < slot.end and exist_slot.end > slot.start:
                busy.append(agg)
        return busy


class InMemoryTablesRepository(TablesRepository):
    def __init__(self) -> None:
        self._items: List[dict]

    def get_free_tables(self, slot: TimeSlot) -> List[dict]:
        return [
            {"id": "T1", "capacity": 2},
            {"id": "T2", "capacity": 4},
        ]


# Заготовка под SQLAlchemy (для лекции / дальнейшего расширения)
class SqlAlchemyReservationRepository(ReservationRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, reservation_id: str) -> Optional[ReservationAggregate]:
        """
        Получает reservation по ид.
        """
        db_model = (
            self.session.query(ReservationDBModel).filter_by(id=reservation_id).first()
        )
        if not db_model:
            return None

        slot = TimeSlot(start=db_model.slot_start, end=db_model.slot_end)
        party_size = PartySize(db_model.party_size)
        table_id = TableId(db_model.table_id) if db_model.table_id else None

        root_entity = Reservation(
            reservation_id=db_model.id,
            slot=slot,
            party_size=party_size,
            table_id=table_id,
            status=ReservationStatus(db_model.status),
        )

        return ReservationAggregate(root=root_entity)

    def add(self, reservation_agg: ReservationAggregate) -> None:
        """
        Добавляет новый reservation.
        """
        root = reservation_agg.root

        db_model = ReservationDBModel(
            id=root.id,
            slot_start=root.slot.start,
            slot_end=root.slot.end,
            party_size=root.party_size.value,
            table_id=root.table_id.value if root.table_id else None,
            status=root.status.value,
        )

        self.session.add(db_model)

    def save(self, reservation_agg: ReservationAggregate) -> None:
        """
        Сохраняет изменения.
        """
        root = reservation_agg.root
        db_model = self.session.query(ReservationDBModel).filter_by(id=root.id).first()

        if not db_model:
            raise ValueError("Бронь не найдена")

        db_model.slot_start = root.slot.start
        db_model.slot_end = root.slot.end
        db_model.party_size = root.party_size.value
        db_model.table_id = root.table_id.value if root.table_id else None
        db_model.status = root.status.value

    def list_for_slot(self, slot: TimeSlot) -> List[ReservationAggregate]:
        """
        Возвращает список по временному промежутку.
        """
        results = (
            self.session.query(ReservationDBModel)
            .filter(
                ReservationDBModel.slot_start < slot.end,
                ReservationDBModel.slot_end > slot.start,
            )
            .all()
        )

        aggregates = []
        for db_model in results:
            slot = TimeSlot(start=db_model.slot_start, end=db_model.slot_end)
            ps = PartySize(db_model.party_size)
            tid = TableId(db_model.table_id) if db_model.table_id else None

            root = Reservation(
                reservation_id=db_model.id,
                slot=slot,
                party_size=ps,
                table_id=tid,
                status=ReservationStatus(db_model.status),
            )
            aggregates.append(ReservationAggregate(root=root))

        return aggregates


class SqlAlchemyTablesRepository(TablesRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_free_tables(self, slot: TimeSlot) -> List[dict]:
        """
        Получает свободные столы (по времени и статусу).
        """
        busy_tables_query = (
            self.session.query(ReservationDBModel.table_id)
            .filter(
                and_(
                    ReservationDBModel.table_id.isnot(None),
                    ReservationDBModel.status.notin_(["CANCELLED", "COMPLETED"]),
                    ReservationDBModel.slot_start < slot.end,
                    ReservationDBModel.slot_end > slot.start,
                )
            )
            .distinct()
        )

        free_tables = (
            self.session.query(TableDBModel)
            .filter(TableDBModel.id.notin_(busy_tables_query))
            .all()
        )

        return [{"id": t.id, "capacity": t.capacity} for t in free_tables]
