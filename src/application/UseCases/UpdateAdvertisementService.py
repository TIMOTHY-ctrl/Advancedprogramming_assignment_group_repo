from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Domain.Aggregate.TripAdvatAggregate.TripAdvertisement import TripAdvertisement
from src.Domain.Events.TripFullyBooked import TripFullyBooked
from src.application.EventHandlers.TripFullyBookedHandler import (
    TripFullyBookedHandler,
)
from src.application.Repositories.ITripAdvertisementRepository import (
    ITripAdvertisementRepository,
)


class UpdateAdvertisementService:
    def __init__(
        self,
        advertisement_repository: ITripAdvertisementRepository,
        fully_booked_handler: TripFullyBookedHandler,
    ) -> None:
        self._advertisement_repository = advertisement_repository
        self._fully_booked_handler = fully_booked_handler

    def refresh(
        self, trip: Trip, event: TripFullyBooked | None = None
    ) -> None:
        if event is not None:
            self._fully_booked_handler.handle(event)
            return
        if trip.has_available_seats:
            self._advertisement_repository.put(
                TripAdvertisement(
                    trip_number=trip.trip_number,
                    departure_time=trip.departure_time,
                    available_seats=trip.available_seats,
                )
            )
        else:
            self._advertisement_repository.remove(trip.trip_number)