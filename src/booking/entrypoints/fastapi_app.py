"""
Контроллер под FastApi
"""

from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, Field

from booking.application.commands import (
    CancelReservation,
    ChangeTimeSlotReservation,
    CompletedReservation,
    CreateReservation,
)
from booking.application.handlers import (
    CancelReservationHandler,
    ChangeTimeSlotReservationHandler,
    CompletedReservationHandler,
    CreateReservationHandler,
)
from booking.domain.services import TableAllocationService
from booking.infrastructure.database.db import SessionLocal
from booking.infrastructure.uow import SqlAlchemyUnitOfWork

app = FastAPI(title="Restaurant Booking")


class CreateReservationDTO(BaseModel):
    slot_start: datetime = Field(..., description="Время начала брони")
    duration_min: int = Field(..., description="Продолжительность брони")
    party_size: int = Field(..., description="Количество человек")


class CancelReservationDTO(BaseModel):
    reservation_id: str = Field(..., description="Идентификатор брони")


class CompletedReservationDTO(BaseModel):
    reservation_id: str = Field(..., description="Идентификатор брони")


class ChangeTimeSlotReservationDTO(BaseModel):
    reservation_id: str = Field(..., description="Идентификатор брони")
    slot_start: datetime = Field(..., description="Время начала брони")
    duration_min: int = Field(..., description="Продолжительность брони")


@app.post("/reservations", summary="Создать бронь", tags=["Booking"])
def create_reservation(dto: CreateReservationDTO) -> dict[str, str]:
    handler = CreateReservationHandler(
        SqlAlchemyUnitOfWork(SessionLocal), TableAllocationService()
    )
    cmd = CreateReservation(**dto.dict())
    try:
        reservation_id = handler(cmd)
        return {
            "message": f"Ваша бронь создана, {reservation_id}",
            "reservation_id": reservation_id,
        }
    except ValueError as e:
        return {"message": str(e)}


@app.post("/cancel_reservation", summary="Отменить бронь", tags=["Booking"])
def cancel_reservation(dto: CancelReservationDTO) -> dict[str, str]:
    handler = CancelReservationHandler(SqlAlchemyUnitOfWork(SessionLocal))
    cmd = CancelReservation(**dto.dict())
    try:
        handler(cmd)
        return {"message": f"Бронь {cmd.reservation_id} отменена"}
    except ValueError as e:
        return {"message": str(e)}


@app.post("/mark_completed", summary="Закрыть бронь", tags=["Booking"])
def mark_completed(dto: CompletedReservationDTO) -> dict[str, str]:
    handler = CompletedReservationHandler(SqlAlchemyUnitOfWork(SessionLocal))
    cmd = CompletedReservation(**dto.dict())
    try:
        handler(cmd)
        return {"message": f"Бронь {cmd.reservation_id} закрыта"}
    except ValueError as e:
        return {"message": str(e)}


@app.post("/change_timeslot", summary="Изменить вермя бронирования", tags=["Booking"])
def change_timeslot(dto: ChangeTimeSlotReservationDTO) -> dict[str, str]:
    handler = ChangeTimeSlotReservationHandler(SqlAlchemyUnitOfWork(SessionLocal))
    cmd = ChangeTimeSlotReservation(**dto.dict())
    try:
        handler(cmd)
        return {"message": f"Время бронирования {cmd.reservation_id} изменено"}
    except ValueError as e:
        return {"message": str(e)}
