from datetime import datetime

from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Domain.Entities.bus import Bus
from src.application.Repositories.ITripRepository import ITripRepository
from src.application.Ports.Workflow import AdvertisementUpdater, SchedulingPolicy, UnitOfWork


class CreateTripService:
    def __init__(
        self,
        trip_repository: ITripRepository,
        advertisement_service: AdvertisementUpdater,
        scheduling_policy: SchedulingPolicy,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._scheduling_policy = scheduling_policy
        self._unit_of_work = unit_of_work
        self._trip_repository = trip_repository
        self._advertisement_service = advertisement_service

    def execute(
        self, trip_number: str, departure_time: datetime, bus: Bus
    ) -> Trip:
        with self._unit_of_work.transaction():
            if self._trip_repository.find_by_number(trip_number) is not None:
                raise ValueError(f"Trip {trip_number} already exists")

            trip = Trip(trip_number, departure_time, bus)
            departures = self._trip_repository.find_departures(bus.bus_number, departure_time)
            self._scheduling_policy.ensure_available(bus, departure_time, departures)
            self._trip_repository.add(trip)
            self._advertisement_service.refresh(trip)
            return trip
