from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ReservationDBModel(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    slot_start = Column(DateTime, nullable=False)
    slot_end = Column(DateTime, nullable=False)
    party_size = Column(Integer, nullable=False)
    table_id = Column(String, ForeignKey("tables.id"), nullable=True)
    status = Column(String, default="CREATED")


class TableDBModel(Base):
    __tablename__ = "tables"

    id = Column(String, primary_key=True)
    capacity = Column(Integer, nullable=False)
