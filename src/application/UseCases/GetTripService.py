from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.application.Repositories.ITripRepository import ITripRepository


class GetTripService:
    def __init__(self, trip_repository: ITripRepository) -> None:
        self._trip_repository = trip_repository

    def execute(self, trip_number: str) -> Trip:
        trip = self._trip_repository.find_by_number(trip_number)
        if trip is None:
            raise ValueError(f"Trip {trip_number} does not exist")
        return trip
