from datetime import datetime

from booking.application.commands import CompletedReservation
from booking.application.handlers import CompletedReservationHandler
from booking.domain.model import (
    PartySize,
    Reservation,
    ReservationAggregate,
    ReservationStatus,
    TableId,
    TimeSlot,
)
from booking.infrastructure.uow import InMemoryUnitOfWork


def test_completed_reservation_happy_path(
    uow: InMemoryUnitOfWork, created_reservation_id: str
) -> None:
    res_agg = uow.reservations.get(created_reservation_id)
    assert res_agg is not None

    completed_cmd = CompletedReservation(reservation_id=created_reservation_id)
    completed_handler = CompletedReservationHandler(uow)
    completed_handler(completed_cmd)

    completed_res = uow.reservations.get(created_reservation_id)
    assert uow.committed is True
    assert completed_res is not None
    assert completed_res.root.status == ReservationStatus.COMPLETED


def test_cancel_reservation_if_cancelled() -> None:
    root_entity = Reservation(
        reservation_id="example",
        slot=TimeSlot(start=datetime.now(), end=datetime.now()),
        party_size=PartySize(2),
        table_id=TableId("T1"),
        status=ReservationStatus.CANCELLED,
    )

    agg = ReservationAggregate(root=root_entity)

    uow = InMemoryUnitOfWork()
    uow.reservations.add(agg)
    cancel_handler = CompletedReservationHandler(uow)
    cancel_cmd = CompletedReservation(reservation_id=root_entity.id)

    try:
        cancel_handler(cancel_cmd)
        assert False, "Invariant: can complete only CONFIRMED reservation"
    except ValueError:
        assert True
