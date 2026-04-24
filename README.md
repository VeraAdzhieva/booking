# Restaurant Booking (DDD + Clean Architecture)


## Структура
- `src/booking/domain` — доменная модель (Entity/VO/Aggregate Root), инварианты, события, доменные сервисы, порты (Repository).
- `src/booking/application` — use-cases (handlers), Unit of Work порт.
- `src/booking/infrastructure` — адаптеры (in-memory repo/uow), заготовки под SQLAlchemy.
- `src/booking/entrypoints` — пример HTTP entrypoint (FastAPI).


## Доменные термины (Ubiquitous Language)
- Reservation — бронь
- TimeSlot — временной слот (start/end)
- PartySize — количество гостей
- TableId — идентификатор стола
- ReservationStatus — статус брони
