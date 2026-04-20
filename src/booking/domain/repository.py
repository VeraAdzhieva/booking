from __future__ import annotations

from typing import List, Optional, Protocol

from .model import ReservationAggregate, TimeSlot


# Repository Port (выходной порт)
class ReservationRepository(Protocol):
    def get(self, reservation_id: str) -> Optional[ReservationAggregate]:
        pass

    def save(self, reservation: ReservationAggregate) -> None:
        pass

    def add(self, reservation: ReservationAggregate) -> None:
        pass

    def list_for_slot(self, slot: TimeSlot) -> List[ReservationAggregate]:
        pass


class TablesRepository(Protocol):
    def get_free_tables(self, slot: TimeSlot) -> List[dict]:
        pass
