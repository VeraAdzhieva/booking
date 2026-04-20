from datetime import datetime

from booking.application.commands import CancelReservation
from booking.application.handlers import CancelReservationHandler
from booking.domain.model import (
    PartySize,
    Reservation,
    ReservationAggregate,
    ReservationStatus,
    TableId,
    TimeSlot,
)
from booking.infrastructure.uow import InMemoryUnitOfWork


def test_cancel_reservation_happy_path(
    uow: InMemoryUnitOfWork, created_reservation_id: str
) -> None:
    res_agg = uow.reservations.get(created_reservation_id)
    assert res_agg is not None
    assert res_agg.root.status != ReservationStatus.CANCELLED

    cancel_cmd = CancelReservation(reservation_id=created_reservation_id)
    cancel_handler = CancelReservationHandler(uow)
    cancel_handler(cancel_cmd)

    cancel_res = uow.reservations.get(created_reservation_id)
    assert uow.committed is True
    assert cancel_res is not None
    assert cancel_res.root.status == ReservationStatus.CANCELLED


def test_cancel_reservation_not_reserve() -> None:
    uow = InMemoryUnitOfWork()
    handler = CancelReservationHandler(uow)

    cmd = CancelReservation(reservation_id="example")

    try:
        handler(cmd)
        assert False, "Бронь не найдена"
    except ValueError:
        assert True


def test_cancel_reservation_if_completed() -> None:
    root_entity = Reservation(
        reservation_id="example",
        slot=TimeSlot(start=datetime.now(), end=datetime.now()),
        party_size=PartySize(2),
        table_id=TableId("T1"),
        status=ReservationStatus.COMPLETED,
    )

    agg = ReservationAggregate(root=root_entity)

    uow = InMemoryUnitOfWork()
    uow.reservations.add(agg)
    cancel_handler = CancelReservationHandler(uow)
    cancel_cmd = CancelReservation(reservation_id=root_entity.id)

    try:
        cancel_handler(cancel_cmd)
        assert False, "Invariant: cannot cancel COMPLETED reservation"
    except ValueError:
        assert True
