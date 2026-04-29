from __future__ import annotations

from datetime import timedelta

from booking.application.commands import (
    CancelReservation,
    ChangeTimeSlotReservation,
    CompletedReservation,
    CreateReservation,
)
from booking.application.unit_of_work import UnitOfWork
from booking.domain.factory import ReservationFactory
from booking.domain.model import TimeSlot
from booking.domain.services import TableAllocationService


class CreateReservationHandler:
    """
    Создает бронь.
    """

    def __init__(self, uow: UnitOfWork, allocator: TableAllocationService):
        self.uow = uow
        self.allocator = allocator

    def __call__(self, cmd: CreateReservation) -> str:
        reservation_agg = ReservationFactory.create(
            slot_start=cmd.slot_start,
            duration_min=cmd.duration_min,
            party_size=cmd.party_size,
        )
        reservation = reservation_agg.root

        with self.uow:
            tables = self.uow.tables.get_free_tables(reservation.slot)
            table_id = self.allocator.allocate(reservation, tables)
            reservation_agg.assign_table(table_id)
            reservation_agg.confirm()

            assert self.uow.reservations is not None
            self.uow.reservations.add(reservation_agg)
            self.uow.commit()

        return reservation.id


class CancelReservationHandler:
    """
    Отменяет бронь.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def __call__(self, cmd: CancelReservation) -> bool:
        with self.uow:
            reservation_agg = self.uow.reservations.get(cmd.reservation_id)
            if not reservation_agg:
                raise ValueError("Бронь не найдена")
            reservation_agg.cancel()
            self.uow.reservations.save(reservation_agg)
            self.uow.commit()

        return True


class CompletedReservationHandler:
    """
    Закрывает бронь.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def __call__(self, cmd: CompletedReservation) -> bool:
        with self.uow:
            reservation_agg = self.uow.reservations.get(cmd.reservation_id)
            if not reservation_agg:
                raise ValueError("Бронь не найдена")
            reservation_agg.mark_completed()
            self.uow.reservations.save(reservation_agg)
            self.uow.commit()

        return True


class ChangeTimeSlotReservationHandler:
    """
    Изменяет время брони.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def __call__(self, cmd: ChangeTimeSlotReservation) -> bool:
        with self.uow:
            reservation_agg = self.uow.reservations.get(cmd.reservation_id)
            if not reservation_agg:
                raise ValueError("Бронь не найдена")

            time_slot = TimeSlot(
                start=cmd.slot_start,
                end=cmd.slot_start + timedelta(minutes=cmd.duration_min),
            )
            reservs_for_slot = self.uow.reservations.list_for_slot(time_slot)
            for reservs in reservs_for_slot:
                if reservs.root.id == cmd.reservation_id:
                    continue

                if reservs.root.table_id == reservation_agg.root.table_id:
                    raise ValueError("Время бронирования занято")

            reservation_agg.change_reservation_time(cmd.slot_start, cmd.duration_min)
            self.uow.reservations.save(reservation_agg)
            self.uow.commit()

        return True
