from datetime import datetime
from typing import Protocol

from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Domain.Aggregate.TripAdvatAggregate.TripAdvertisement import TripAdvertisement
from src.Domain.Entities.bus import Bus
from src.application.DTOs.BookSeatInputDTO import BookSeatInputDTO
from src.application.DTOs.BookSeatOutputDTO import BookSeatOutputDTO


class BookSeatUseCase(Protocol):
    def execute(self, request: BookSeatInputDTO) -> BookSeatOutputDTO: ...


class GetTripUseCase(Protocol):
    def execute(self, trip_number: str) -> Trip: ...


class ListAvailableTripsUseCase(Protocol):
    def execute(self) -> list[TripAdvertisement]: ...


class CreateTripUseCase(Protocol):
    def execute(
        self, trip_number: str, departure_time: datetime, bus: Bus
    ) -> Trip: ...
