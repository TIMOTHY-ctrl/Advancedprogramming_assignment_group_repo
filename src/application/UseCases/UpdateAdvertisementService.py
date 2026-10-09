from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Domain.Aggregate.TripAdvatAggregate.TripAdvertisement import TripAdvertisement
from src.Domain.Events.TripFullyBooked import TripFullyBooked
from src.application.EventHandlers.TripFullyBookedHandler import TripFullyBookedHandler
from src.application.Repositories.ITripAdvertisementRepository import ITripAdvertisementRepository


class UpdateAdvertisementService:
    def __init__(self, advertisement_repository: ITripAdvertisementRepository,
                 fully_booked_handler: TripFullyBookedHandler) -> None:
        self._advertisement_repository = advertisement_repository
        self._fully_booked_handler = fully_booked_handler

    def refresh(self, trip: Trip, event: TripFullyBooked | None = None) -> str:
        if event is not None:
            return self._fully_booked_handler.handle(event)
        existing = self._advertisement_repository.find_by_number(trip.trip_number)
        if existing is None:
            advertisement = TripAdvertisement(trip.trip_number, trip.departure_time,
                                               trip.available_seats)
        else:
            advertisement = existing.update_availability(trip.available_seats)
        self._advertisement_repository.put(advertisement)
        return 'advertised'
