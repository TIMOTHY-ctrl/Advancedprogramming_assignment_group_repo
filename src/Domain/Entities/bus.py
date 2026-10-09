from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class Bus:
    bus_number: str
    capacity: int

    def __post_init__(self) -> None:
        if not isinstance(self.bus_number, str) or not self.bus_number.strip():
            raise ValueError("Bus number cannot be empty")
        if isinstance(self.capacity, bool) or not isinstance(self.capacity, int):
            raise ValueError("Bus capacity must be a positive integer")
        if self.capacity <= 0:
            raise ValueError("Bus capacity must be a positive integer")
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bus) or type(other) is not type(self):
            return NotImplemented
        return self.bus_number == other.bus_number

    def __hash__(self) -> int:
        return hash((type(self), self.bus_number))
