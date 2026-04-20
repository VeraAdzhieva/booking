from datetime import datetime, timedelta

from booking.application.commands import ChangeTimeSlotReservation
from booking.application.handlers import ChangeTimeSlotReservationHandler
from booking.domain.model import (
    PartySize,
    Reservation,
    ReservationAggregate,
    ReservationStatus,
    TableId,
    TimeSlot,
)
from booking.infrastructure.uow import InMemoryUnitOfWork


def test_change_timeslot_reservation_happy_path(
    uow: InMemoryUnitOfWork, created_reservation_id: str
) -> None:
    res_agg = uow.reservations.get(created_reservation_id)
    assert res_agg is not None
    assert res_agg.root.status not in [
        ReservationStatus.CANCELLED,
        ReservationStatus.COMPLETED,
    ]

    cmd = ChangeTimeSlotReservation(
        reservation_id=created_reservation_id,
        slot_start=datetime(2026, 1, 1, 19, 0, 0),
        duration_min=60,
    )

    handler = ChangeTimeSlotReservationHandler(uow)
    handler(cmd)

    res = uow.reservations.get(created_reservation_id)
    assert uow.committed is True
    assert res is not None

    timeslot = TimeSlot(
        start=cmd.slot_start, end=cmd.slot_start + timedelta(minutes=cmd.duration_min)
    )
    assert res.root.slot == timeslot


def test_cancel_reservation_if_exist(
    uow: InMemoryUnitOfWork, created_reservation_id: str
) -> None:
    res_agg = uow.reservations.get(created_reservation_id)
    assert res_agg is not None
    assert res_agg.root.status not in [
        ReservationStatus.CANCELLED,
        ReservationStatus.COMPLETED,
    ]
    assert res_agg.root.table_id is not None

    root_entity = Reservation(
        reservation_id="example",
        slot=TimeSlot(
            start=datetime(2026, 1, 1, 19, 0, 0), end=datetime(2026, 1, 1, 20, 30, 0)
        ),
        party_size=PartySize(res_agg.root.party_size.value),
        table_id=TableId(res_agg.root.table_id.value),
        status=ReservationStatus.CONFIRMED,
    )

    agg = ReservationAggregate(root=root_entity)
    uow.reservations.add(agg)

    handler = ChangeTimeSlotReservationHandler(uow)
    cmd = ChangeTimeSlotReservation(
        reservation_id=created_reservation_id,
        slot_start=datetime(2026, 1, 1, 19, 0, 0),
        duration_min=30,
    )

    try:
        handler(cmd)
        assert False, "Время бронирования занято"
    except ValueError:
        assert True
