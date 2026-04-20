from datetime import datetime

import pytest

from src.booking.application.commands import CreateReservation
from src.booking.application.handlers import CreateReservationHandler
from src.booking.domain.services import TableAllocationService
from src.booking.infrastructure.uow import InMemoryUnitOfWork


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.fixture
def created_reservation_id(uow: InMemoryUnitOfWork) -> str:
    allocator = TableAllocationService()
    handler = CreateReservationHandler(uow=uow, allocator=allocator)

    cmd = CreateReservation(
        slot_start=datetime(2030, 1, 1, 19, 0, 0),
        duration_min=90,
        party_size=3,
    )

    reservation_id = handler(cmd)
    return reservation_id
