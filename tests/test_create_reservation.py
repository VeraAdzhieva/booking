from datetime import datetime

from booking.application.commands import CreateReservation
from booking.application.handlers import CreateReservationHandler
from booking.domain.services import TableAllocationService
from booking.infrastructure.uow import InMemoryUnitOfWork


def test_create_reservation_happy_path() -> None:
    uow = InMemoryUnitOfWork()
    handler = CreateReservationHandler(uow, TableAllocationService())

    cmd = CreateReservation(
        slot_start=datetime(2030, 1, 1, 19, 0, 0),
        duration_min=90,
        party_size=3,
    )

    reservation_id = handler(cmd)

    assert reservation_id
    assert uow.committed is True

    saved = uow.reservations.get(reservation_id)
    assert saved is not None
    assert saved.root.status.value == "CONFIRMED"
    assert saved.root.table_id is not None
    assert saved.root.table_id.value == "T2"


def test_timeslot_invariant_enforced() -> None:
    uow = InMemoryUnitOfWork()
    handler = CreateReservationHandler(uow, TableAllocationService())

    cmd = CreateReservation(
        slot_start=datetime(2030, 1, 1, 19, 0, 0),
        duration_min=-10,
        party_size=2,
    )

    try:
        handler(cmd)
        assert False, "Expected ValueError"
    except ValueError:
        assert True
