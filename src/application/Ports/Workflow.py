from collections.abc import Iterable
from contextlib import AbstractContextManager
from datetime import datetime
from typing import Protocol

from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Domain.Entities.bus import Bus
from src.Domain.Events.TripFullyBooked import TripFullyBooked
from src.application.DTOs.AdvertisementOutcome import AdvertisementOutcome


class UnitOfWork(Protocol):
    """Serialize a workflow; roll back both repositories on exceptions."""

    def transaction(self) -> AbstractContextManager[None]: ...


class AdvertisementUpdater(Protocol):
    def refresh(self, trip: Trip, event: TripFullyBooked | None = None) -> AdvertisementOutcome: ...


class FullyBookedHandler(Protocol):
    def handle(self, event: TripFullyBooked) -> AdvertisementOutcome: ...


class SchedulingPolicy(Protocol):
    def ensure_available(self, bus: Bus, departure_time: datetime,
                         existing_trips: Iterable[Trip]) -> None: ...
