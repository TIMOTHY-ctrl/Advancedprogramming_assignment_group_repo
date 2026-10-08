from dataclasses import dataclass


@dataclass(frozen=True)
class Bus:
    bus_number: str
    capacity: int

    def __post_init__(self) -> None:
        if not self.bus_number.strip():
            raise ValueError("Bus number cannot be empty")
        if isinstance(self.capacity, bool) or not isinstance(self.capacity, int):
            raise ValueError("Bus capacity must be a positive integer")
        if self.capacity <= 0:
            raise ValueError("Bus capacity must be a positive integer")