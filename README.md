# Restaurant Booking (DDD + Clean Architecture)

## Запуск 
Запуск сервера: ```poetry run uvicorn booking.entrypoints.fastapi_app:app --reload```
Переход на ```http://127.0.0.1:8000/docs```
Выполнение запросов: 
 - /reservations - Создание брони
 - /cancel_reservation - Отмена брони
 - /mark_completed - Закрыть бронь
 - /change_timeslot - Изменение времени бронирования

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
