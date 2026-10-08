from dataclasses import dataclass


@dataclass(frozen=True)
class TripFullyBooked:
    trip_number: str